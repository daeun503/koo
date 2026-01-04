from abc import ABC, abstractmethod
from pathlib import Path

from app.enums import Domain, SourceType
from app.models.base import Chunk, Document


class SourceIngestor(ABC):
    source_type: SourceType

    def __init__(
        self,
        domain: Domain,
        source_id: str,
        title: str | None,
        content: str | None,
    ):
        self.domain = domain
        self.source_id = source_id
        self.title = title
        self.content = content

    @abstractmethod
    def build_document(self) -> Document: ...

    @staticmethod
    def chunking(text: str, max_chars: int = 900) -> list[str]:
        lines = [ln.strip() for ln in text.splitlines()]
        lines = [ln for ln in lines if ln]

        chunks: list[str] = []
        buf: list[str] = []
        size = 0

        for ln in lines:
            if size + len(ln) + 1 > max_chars and buf:
                chunks.append("\n".join(buf))
                buf, size = [], 0
            buf.append(ln)
            size += len(ln) + 1

        if buf:
            chunks.append("\n".join(buf))
        return chunks

    def get_chunks(self, doc: Document) -> list[Chunk]:
        chunks = self.chunking(doc.raw_content)
        out: list[Chunk] = []

        for idx, text in enumerate(chunks):
            chunk = Chunk(
                chunk_index=idx,
                chunk_text=text,
                chunk_hash="",
                token_len=0,
            )
            out.append(chunk)

        return out


class RawTextIngestor(SourceIngestor):
    source_type = SourceType.RAW_TEXT

    def build_document(self) -> Document:
        return Document(
            domain=self.domain,
            source_type=self.source_type,
            source_id=self.source_id,
            title=self.title,
            raw_content=self.content,
            content_hash="",
            version=1,
        )


class FileIngestor(SourceIngestor):
    source_type = SourceType.FILE

    def build_document(self) -> Document:
        path = Path(self.source_id)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not path.is_file():
            raise ValueError(f"Not a file: {path}")

        raw = path.read_text(encoding="utf-8")
        return Document(
            domain=self.domain,
            source_type=self.source_type,
            source_id=str(path),
            title=path.name,
            raw_content=raw,
            content_hash="",
            version=1,
        )


class IngestorFactory:
    @staticmethod
    def create(
        domain: Domain,
        source_type: SourceType,
        source_id: str,
        title: str | None,
        content: str | None,
    ) -> SourceIngestor:
        default_args = {
            "domain": domain,
            "source_id": source_id,
            "title": title,
            "content": content,
        }
        match source_type:
            case SourceType.GITHUB:
                raise NotImplementedError()
            case SourceType.SLACK:
                raise NotImplementedError()
            case SourceType.NOTION:
                raise NotImplementedError("Notion ingestor not implemented")
            case SourceType.RAW_TEXT:
                return RawTextIngestor(**default_args)
            case SourceType.FILE:
                return FileIngestor(**default_args)
