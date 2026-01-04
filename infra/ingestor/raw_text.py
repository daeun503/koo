from app.enums import SourceType
from app.models.base import Document
from app.repositories.ingestor import Ingestor


class RawTextIngestor(Ingestor):
    source_type = SourceType.RAW_TEXT

    def build_document(self) -> Document:
        return Document(
            domain=self.domain,
            source_type=self.source_type,
            source_id=self.source_id,
            title=self.title,
            raw_content=self.content,
        )
