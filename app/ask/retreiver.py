import hashlib
import re
from typing import Any

from app.enums import Domain, RouterDomain
from app.repository.chunk import ChunkRepository
from app.repository.vector_store import VectorStoreRepository
from config import settings


def embed_text(text: str) -> list[float]:
    """
    MVP: 더미 임베딩.
    - text를 sha256으로 시드 삼아 재현 가능한 벡터를 생성
    - 실제 임베딩(OpenAI 등)으로 교체 예정
    """
    dim = settings.EMBEDDING_DIM
    h = hashlib.sha256(text.encode("utf-8")).digest()  # 32 bytes

    vec: list[float] = []
    for i in range(dim):
        b = h[i % 32]
        vec.append((b / 255.0) * 2.0 - 1.0)  # [-1, 1]
    return vec


class Retriever:
    def __init__(
        self,
        chunk_repo: ChunkRepository,
        vector_store_repo: VectorStoreRepository,
    ):
        self.chunk_repo = chunk_repo
        self.vector_store_repo = vector_store_repo

    def route_to_domain(
        self,
        query,
    ) -> RouterDomain:
        s = query.lower()

        dev_signals = [
            r"\btraceback\b",
            r"\bexception\b",
            r"\berror\b",
            r"\bcommit\b",
            r"\bpr\b",
            r"[0-9a-f]{7,40}",  # commit hash
            r"\.py\b|\.ts\b|\.js\b|\.go\b|\.java\b",
            r"\bfunction\b|\bclass\b|\bmodule\b",
        ]
        cs_signals = [
            r"\b환불\b",
            r"\b정책\b",
            r"\b문의\b",
            r"\b고객\b",
            r"\b안내\b",
            r"\bcs\b",
            r"\bfaq\b",
        ]

        dev_hit = any(re.search(p, s) for p in dev_signals)
        cs_hit = any(re.search(p, s) for p in cs_signals)

        if dev_hit and cs_hit:
            return RouterDomain.MIXED
        if dev_hit:
            return RouterDomain.DEV
        if cs_hit:
            return RouterDomain.CS
        return RouterDomain.MIXED

    def retrieve(
        self,
        domain: Domain,
        query: str,
        topk: int | None = None,
        *,
        filter_expr: str | None = None,
    ) -> list[dict[str, Any]]:
        k = topk or settings.TOPK

        pairs = self.vector_store_repo.search(
            domain=domain,
            embedding=embed_text(query),
            top_k=k,
            filter_expr=filter_expr,
        )
        if not pairs:
            return []

        chunk_ids = [cid for cid, _ in pairs]
        chunks = self.chunk_repo.get_by_ids(chunk_ids)
        chunk_map = {chunk.id: chunk for chunk in chunks}

        enriched: list[dict[str, Any]] = []
        for cid, score in pairs:
            chunk = chunk_map.get(int(cid))
            if not chunk:
                continue

            enriched.append(
                {
                    "chunk_id": chunk.id,
                    "score": float(score),
                    "chunk_text": chunk.chunk_text,
                }
            )

        enriched.sort(key=lambda x: x["score"], reverse=True)
        return enriched

    def get_hits(
        self,
        route: RouterDomain,
        query: str,
        topk: int | None = None,
        *,
        filter_expr: str | None = None,
    ) -> list[dict[str, Any]]:
        if route == RouterDomain.MIXED:
            cs_hits = self.retrieve(Domain.CS, query, topk=topk, filter_expr=filter_expr)
            dev_hits = self.retrieve(Domain.DEV, query, topk=topk, filter_expr=filter_expr)
            hits = cs_hits + dev_hits
        else:
            domain = Domain.CS if route == RouterDomain.CS else Domain.DEV
            hits = self.retrieve(domain, query, topk=topk, filter_expr=filter_expr)

        hits.sort(key=lambda x: x["score"], reverse=True)

        return hits[:topk]
