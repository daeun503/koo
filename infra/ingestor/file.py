from pathlib import Path

from app.enums import SourceType
from app.models.base import Document
from app.repositories.ingestor import Ingestor


class FileIngestor(Ingestor):
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
        )
