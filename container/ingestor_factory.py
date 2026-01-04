from app.enums import Domain, SourceType
from app.repositories.ingestor import Ingestor


class IngestorFactory:
    def create(
        self,
        domain: Domain,
        source_type: SourceType,
        source_id: str,
        *,
        title: str | None = None,
        content: str | None = None,
    ) -> Ingestor:
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
                from infra.ingestor.notion import NotionIngestor

                return NotionIngestor(**default_args)
            case SourceType.RAW_TEXT:
                from infra.ingestor.raw_text import RawTextIngestor

                return RawTextIngestor(**default_args)
            case SourceType.FILE:
                from infra.ingestor.file import FileIngestor

                return FileIngestor(**default_args)
