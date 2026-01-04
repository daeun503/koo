import json
from dataclasses import dataclass, field

from app.enums import Domain, SourceType


@dataclass(slots=True)
class Document:
    domain: Domain
    source_type: SourceType
    source_id: str

    title: str | None
    raw_content: str

    content_hash: str | None = None
    version: int = 1
    id: int | None = None


@dataclass(slots=True)
class Chunk:
    chunk_index: int
    chunk_text: str
    chunk_hash: str = ""

    id: int | None = None
    document_id: int | None = None
    context_id: int = 0


@dataclass(slots=True)
class VectorSearchChunk:
    chunk_id: int
    chunk: Chunk
    score: float
    domain: Domain


@dataclass(slots=True)
class QueryLog:
    id: int | None

    query_text: str
    topk: int

    selected_chunk_ids: list[int] | None = None
    expended_chunk_ids: list[int] | None = None
    answer: str | None = None


@dataclass
class QueryLogMeta:
    topk: int
    hit_chunk_ids: dict[Domain, list[int]] = field(default_factory=dict)
    selected_chunk_ids: list[int] = field(default_factory=list)
    expended_chunk_ids: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "topk": self.topk,
            "hit_chunk_ids": {domain.value: chunk_ids for domain, chunk_ids in self.hit_chunk_ids.items()},
            "selected_chunk_ids": self.selected_chunk_ids,
            "expended_chunk_ids": self.expended_chunk_ids,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)
