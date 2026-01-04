from typing import Protocol

from app.enums import Domain, SourceType


class VectorStoreRepository(Protocol):
    def upsert(
        self,
        domain: Domain,
        source_type: SourceType,
        chunk_id: int,
        embedding: list[float],
    ) -> None: ...

    def bulk_upsert(
        self,
        domain: Domain,
        source_type: SourceType,
        chunk_ids: list[int],
        embeddings: list[list[float]],
    ) -> None: ...

    def delete(self, domain: Domain, chunk_id: int) -> None: ...

    def search(
        self,
        domain: Domain,
        embedding: list[float],
        top_k: int,
        filter_expr: str | None = None,
    ) -> list[tuple[int, float]]: ...
