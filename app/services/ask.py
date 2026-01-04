from collections import defaultdict
from dataclasses import dataclass

from rich.console import Console
from rich.table import Table

from app.enums import Domain
from app.models.base import QueryLogMeta, VectorSearchChunk
from app.repositories.chunk import ChunkRepository
from app.repositories.llm import Answerer, Embedder
from app.repositories.query_log import QueryLogRepository
from app.repositories.vector_store import VectorStoreRepository

__all__ = ["AskService"]


@dataclass(slots=True)
class AskResult:
    answer: str
    hits: list[VectorSearchChunk]


class AskService:
    def __init__(
        self,
        chunk_repo: ChunkRepository,
        query_log_repo: QueryLogRepository,
        vector_store_repo: VectorStoreRepository,
        embedder: Embedder,
        answerer: Answerer,
        topk: int,
    ):
        self.chunk_repo = chunk_repo
        self.query_log_repo = query_log_repo
        self.vector_store_repo = vector_store_repo
        self.embedder = embedder
        self.answerer = answerer
        self.topk = topk

    def ask(self, question: str) -> AskResult:
        query_log = self.query_log_repo.create(
            query_text=question,
            topk=self.topk,
        )

        # 벡터 서치 및 답변 생성
        hits = self.search_all_domain(query=question)

        selected = hits[: self.topk]
        contexts = self._expand_by_context(selected)

        output, usage = self.answerer.answer(question=question, contexts=contexts)

        # meta 정보 구성
        hit_chunk_ids = defaultdict(list)
        for hit in hits:
            hit_chunk_ids[hit.domain].append(hit.chunk_id)
        meta = QueryLogMeta(
            topk=self.topk,
            hit_chunk_ids=hit_chunk_ids,
            selected_chunk_ids=[c.chunk_id for c in selected],
            expended_chunk_ids=[c.chunk_id for c in contexts],
        )

        # DB 정보 업데이트
        self.query_log_repo.update(
            id=query_log.id,
            selected_chunk_ids=meta.selected_chunk_ids,
            expended_chunk_ids=meta.expended_chunk_ids,
            answer=output.answer,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            meta=meta.to_dict(),
        )

        return AskResult(answer=output.answer, hits=hits)

    def _expand_by_context(self, hits: list[VectorSearchChunk]) -> list[VectorSearchChunk]:
        targets = {(hit.chunk.document_id, hit.chunk.context_id): hit for hit in hits}

        expanded_chunks: list[VectorSearchChunk] = []
        for uk, search_chunk in targets.items():
            search_chunk: VectorSearchChunk
            document_id, context_id = uk

            chunks = self.chunk_repo.list_by_context(
                document_id=document_id,
                context_id=context_id,
            )

            for chunk in chunks:
                expanded_chunks.append(
                    VectorSearchChunk(
                        chunk_id=chunk.id,
                        chunk=chunk,
                        score=search_chunk.score,
                        domain=search_chunk.domain,
                    )
                )

        return expanded_chunks

    def print_answer(
        self,
        console: Console,
        answer: AskResult,
    ):
        table = Table(title=f"koo ask (topk={self.topk})")
        table.add_column("rank", justify="right")
        table.add_column("chunk_id", justify="right")
        table.add_column("score", justify="right")
        table.add_column("chunk_text")

        selected_ids = []
        for idx, hit in enumerate(answer.hits, start=1):
            selected_ids.append(hit.chunk_id)
            preview = hit.chunk.chunk_text.replace("\n", " ")
            if len(preview) > 120:
                preview = preview[:120] + "..."
            table.add_row(str(idx), str(hit.chunk_id), f"{hit.score:.4f}", preview)

        console.print(table)

        console.print("\n[bold]Answer[/bold]")
        console.print(answer.answer)

    def search_similar_chunks(
        self,
        domain: Domain,
        query: str,
        *,
        filter_expr: str | None = None,
    ) -> list[VectorSearchChunk]:
        pairs = self.vector_store_repo.search(
            domain=domain,
            embedding=self.embedder.embed_query(query),
            top_k=self.topk,
            filter_expr=filter_expr,
        )
        if not pairs:
            return []

        chunk_ids = [cid for cid, _ in pairs]

        chunks = self.chunk_repo.get_by_ids(chunk_ids)
        chunk_map = {chunk.id: chunk for chunk in chunks}

        results = []
        for cid, score in pairs:
            chunk = chunk_map.get(int(cid))
            if not chunk:
                continue

            similar_chunk = VectorSearchChunk(
                chunk_id=chunk.id,
                chunk=chunk,
                score=float(score),
                domain=domain,
            )
            results.append(similar_chunk)

        results.sort(key=lambda x: x.score, reverse=True)
        return results

    def search_all_domain(
        self,
        query: str,
        *,
        filter_expr: str | None = None,
    ) -> list[VectorSearchChunk]:
        hits = []
        for domain in Domain:
            result = self.search_similar_chunks(domain, query, filter_expr=filter_expr)
            hits.extend(result)

        hits.sort(key=lambda x: x.score, reverse=True)
        return hits
