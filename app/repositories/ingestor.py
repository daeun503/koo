import re
from abc import ABC, abstractmethod
from typing import ClassVar

from app.enums import Domain, SourceType
from app.models.base import Chunk, Document


class Ingestor(ABC):
    source_type: SourceType
    _MD_HEADING_RE: ClassVar[re.Pattern[str]] = re.compile(r"^(#{1,3})\s+")

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

    def get_chunks(self, doc: Document) -> list[Chunk]:
        pairs = self.context_chunking(doc.raw_content)
        out: list[Chunk] = []

        for idx, (context_id, text) in enumerate(pairs):
            out.append(
                Chunk(
                    chunk_index=idx,
                    chunk_text=text,
                    context_id=context_id,
                )
            )

        return out

    # =============================================
    # Chunking Logic
    # =============================================

    @staticmethod
    def _chunk_lines(lines: list[str], max_chars: int = 900) -> list[str]:
        chunks: list[str] = []
        buf: list[str] = []
        size = 0

        for ln in lines:
            ln = ln.strip()
            if not ln:
                continue

            if size + len(ln) + 1 > max_chars and buf:
                chunks.append("\n".join(buf))
                buf, size = [], 0
            buf.append(ln)
            size += len(ln) + 1

        if buf:
            chunks.append("\n".join(buf))
        return chunks

    @classmethod
    def _split_into_heading_blocks(cls, lines: list[str]) -> list[list[str]]:
        def is_heading_boundary(line: str) -> bool:
            return bool(cls._MD_HEADING_RE.match(line.strip()))

        blocks: list[list[str]] = []
        buf: list[str] = []

        for ln in lines:
            if is_heading_boundary(ln) and buf:
                blocks.append(buf)
                buf = []
            buf.append(ln)

        if buf:
            blocks.append(buf)

        return blocks

    @classmethod
    def context_chunking(cls, text: str, max_chars: int = 900) -> list[tuple[int, str]]:
        lines = [ln.rstrip() for ln in text.splitlines()]
        lines = [ln for ln in lines if ln.strip()]
        if not lines:
            return []

        blocks = cls._split_into_heading_blocks(lines)

        out: list[tuple[int, str]] = []
        for ctx_id, block_lines in enumerate(blocks):
            for chunk_text in cls._chunk_lines(block_lines, max_chars=max_chars):
                out.append((ctx_id, chunk_text))
        return out
