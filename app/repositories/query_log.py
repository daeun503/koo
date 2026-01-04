from typing import Protocol

from app.models.base import QueryLog


class QueryLogRepository(Protocol):
    def create(
        self,
        query_text: str,
        topk: int,
    ) -> QueryLog: ...

    def get(self, *, query_log_id: int) -> QueryLog | None: ...

    def update(
        self,
        id: int,
        selected_chunk_ids: list[int] | None = None,
        expended_chunk_ids: list[int] | None = None,
        answer: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        meta: dict | None = None,
    ) -> QueryLog: ...

    def delete(self, id: int) -> None: ...
