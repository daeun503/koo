from dataclasses import dataclass

from app.enums import Domain, RouterDomain, SourceType


@dataclass(slots=True)
class Document:
    domain: Domain
    source_type: SourceType
    source_id: str

    title: str | None
    raw_content: str
    content_hash: str
    version: int = 1

    id: int | None = None


@dataclass(slots=True)
class Chunk:
    chunk_index: int
    chunk_text: str
    chunk_hash: str
    token_len: int = 0

    id: int | None = None
    document_id: int = None
    context_id: int | None = None


@dataclass(slots=True)
class QueryLog:
    id: int | None

    query_text: str
    router_domain: RouterDomain
    topk: int

    selected_chunk_ids: list[int] | None = None
    answer: str | None = None
