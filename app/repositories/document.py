from typing import Protocol

from app.enums import Domain, SourceType
from app.models.base import Document


class DocumentRepository(Protocol):
    def create(
        self,
        domain: Domain,
        source_type: SourceType,
        source_id: str,
        title: str | None,
        raw_content: str,
    ) -> Document: ...

    def get(self, id: int) -> Document | None: ...

    def get_by_source(
        self,
        source_type: SourceType,
        source_id: str,
    ) -> Document | None: ...

    def update(self, document: Document) -> Document: ...

    def upsert(
        self,
        domain: Domain,
        source_type: SourceType,
        source_id: str,
        title: str | None,
        raw_content: str,
    ) -> Document: ...

    def delete(self, id: int) -> None: ...
