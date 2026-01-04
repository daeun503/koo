from typing import Protocol

from app.enums import RouterDomain
from app.models.base import QueryLog


class QueryLogRepository(Protocol):
    def create(
        self,
        query_text: str,
        router_domain: RouterDomain,
        topk: int,
        selected_chunk_ids: list[int] | None = None,
        answer: str | None = None,
    ) -> QueryLog: ...

    def get(self, *, query_log_id: int) -> QueryLog | None: ...

    def all(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[QueryLog]: ...

    def update(
        self,
        id: int,
        query_text: str | None,
        router_domain: RouterDomain | None,
        topk: int | None,
        selected_chunk_ids: list[int] | None = None,
        answer: str | None = None,
    ) -> QueryLog: ...

    def delete(self, id: int) -> None: ...
