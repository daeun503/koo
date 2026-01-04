import time

from pymilvus import Collection

from app.enums import Domain, SourceType
from app.repositories.vector_store import VectorStoreRepository


class MilvusRepositoryImpl(VectorStoreRepository):
    collection_map = {
        Domain.CS: "koo_cs_chunks",
        Domain.DEV: "koo_dev_chunks",
    }

    @staticmethod
    def to_human_score(raw: float) -> float:
        """
        Milvus COSINE metric raw score -> [0,1]
        - similarity(-1~1) 또는 distance(0~2/0~1) 방어 처리
        """
        # 케이스 A: similarity (-1~1)
        if -1.0001 <= raw <= 1.0001:
            s = (raw + 1.0) / 2.0
            return max(0.0, min(1.0, s))

        # 케이스 B: distance
        s = 1.0 - raw
        return max(0.0, min(1.0, s))

    def _get_collection(self, domain: Domain) -> Collection:
        name = self.collection_map[domain]
        col = Collection(name)
        col.load()
        return col

    @staticmethod
    def _ids_expr(ids: list[int]) -> str:
        # Milvus expr: `chunk_id in [1,2,3]`
        return "[" + ",".join(map(str, ids)) + "]"

    @staticmethod
    def _hit_pk(hit) -> int:
        """
        Milvus search hit에서 primary key(chunk_id) 추출.
        pymilvus 버전에 따라 hit.id / hit.pk / hit.entity 접근이 다를 수 있어 방어.
        """
        pk = getattr(hit, "id", None)
        if pk is None:
            pk = getattr(hit, "pk", None)
        if pk is None:
            ent = getattr(hit, "entity", None)
            if ent is not None:
                try:
                    pk = ent.get("chunk_id")
                except Exception:
                    pk = None
        if pk is None:
            raise RuntimeError("Milvus hit does not contain primary key.")
        return int(pk)

    def upsert(
        self,
        domain: Domain,
        source_type: SourceType,
        chunk_id: int,
        embedding: list[float],
    ) -> None:
        col = self._get_collection(domain)
        col.delete(expr=f"chunk_id in {self._ids_expr([chunk_id])}")

        now = int(time.time())
        data = [
            [chunk_id],
            [embedding],
            [source_type.value],
            [now],
        ]
        col.insert(data)
        col.flush()

    def bulk_upsert(
        self,
        domain: Domain,
        source_type: SourceType,
        chunk_ids: list[int],
        embeddings: list[list[float]],
    ) -> None:
        if not chunk_ids:
            return

        if len(chunk_ids) != len(embeddings):
            raise ValueError("chunk_ids and embeddings must have the same length")

        col = self._get_collection(domain)

        col.delete(expr=f"chunk_id in {self._ids_expr(chunk_ids)}")

        now = int(time.time())
        data = [
            chunk_ids,
            embeddings,
            [source_type.value for _ in chunk_ids],
            [now] * len(chunk_ids),
        ]
        col.insert(data)
        col.flush()

    def delete(self, domain: Domain, chunk_id: int) -> None:
        col = self._get_collection(domain)
        col.delete(expr=f"chunk_id in {self._ids_expr([chunk_id])}")
        col.flush()

    def search(
        self,
        domain: Domain,
        embedding: list[float],
        top_k: int,
        filter_expr: str | None = None,
    ) -> list[tuple[int, float]]:
        col = self._get_collection(domain)
        params = {"metric_type": "COSINE", "params": {"nprobe": 16}}

        results = col.search(
            data=[embedding],
            anns_field="embedding",
            param=params,
            limit=top_k,
            expr=filter_expr,
            output_fields=["source_type", "updated_at"],
        )

        out: list[tuple[int, float]] = []
        for hit in results[0]:
            chunk_id = self._hit_pk(hit)
            score = float(hit.score)
            out.append((chunk_id, score))
        return out
