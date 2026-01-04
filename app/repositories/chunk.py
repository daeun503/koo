from typing import Protocol

from app.models.base import Chunk


class ChunkRepository(Protocol):
    def create(
        self,
        document_id: int,
        context_id: int | None,
        chunk_index: int,
        chunk_text: str,
    ) -> Chunk: ...

    def bulk_create(self, document_id: int, chunks: list[Chunk]) -> list[Chunk]: ...

    def get(self, chunk_id: int) -> Chunk | None: ...

    def get_by_ids(self, chunk_ids: list[int]) -> list[Chunk]: ...

    def list_by_document(
        self,
        document_id: int,
        limit: int = 500,
        offset: int = 0,
    ) -> list[Chunk]: ...

    def list_by_context(
        self,
        document_id: int,
        context_id: int,
    ) -> list[Chunk]: ...

    def delete_by_document(self, document_id: int) -> None: ...
