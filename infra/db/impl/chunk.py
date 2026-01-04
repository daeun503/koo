from sqlalchemy import asc

from app.models.base import Chunk as ChunkModel
from app.repositories.chunk import ChunkRepository
from app.utils import compute_content_hash
from infra.db.base import Session
from infra.db.orm.base import Chunk as ChunkOrm


class ChunkRepositoryImpl(ChunkRepository):
    @staticmethod
    def _to_model(o: ChunkOrm) -> ChunkModel:
        return ChunkModel(
            id=o.id,
            document_id=o.document_id,
            context_id=o.context_id,
            chunk_index=o.chunk_index,
            chunk_text=o.chunk_text,
            chunk_hash=o.chunk_hash,
        )

    def create(
        self,
        document_id: int,
        context_id: int | None,
        chunk_index: int,
        chunk_text: str,
    ) -> ChunkModel:
        o = ChunkOrm(
            document_id=document_id,
            context_id=context_id,
            chunk_index=chunk_index,
            chunk_text=chunk_text,
            chunk_hash=compute_content_hash(chunk_text),
        )
        with Session() as db:
            db.add(o)
            db.commit()
            db.refresh(o)
            return self._to_model(o)

    def bulk_create(self, document_id: int, chunks: list[ChunkModel]) -> list[ChunkModel]:
        if not chunks:
            return []

        objects = [
            ChunkOrm(
                document_id=document_id,
                context_id=c.context_id,
                chunk_index=c.chunk_index,
                chunk_text=c.chunk_text,
                chunk_hash=compute_content_hash(c.chunk_text),
            )
            for c in chunks
        ]
        with Session() as db:
            db.add_all(objects)
            db.commit()
            [db.refresh(o) for o in objects]

        return [self._to_model(o) for o in objects]

    def get(self, id: int) -> ChunkModel | None:
        with Session() as db:
            q = db.query(ChunkOrm).filter(ChunkOrm.id == id).one_or_none()

        return self._to_model(q) if q else None

    def get_by_ids(self, chunk_ids: list[int]) -> list[ChunkModel]:
        if not chunk_ids:
            return []

        with Session() as db:
            q = db.query(ChunkOrm).filter(ChunkOrm.id.in_(chunk_ids)).all()
            return [self._to_model(o) for o in q]

    def list_by_document(
        self,
        document_id: int,
        limit: int = 500,
        offset: int = 0,
    ) -> list[ChunkModel]:
        with Session() as db:
            q = (
                db.query(ChunkOrm)
                .filter(ChunkOrm.document_id == document_id)
                .order_by(ChunkOrm.chunk_index.asc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            return [self._to_model(o) for o in q.all()]

    def list_by_context(self, document_id: int, context_id: int) -> list[ChunkModel]:
        with Session() as db:
            rows = (
                db.query(ChunkOrm)
                .filter(
                    ChunkOrm.document_id == document_id,
                    ChunkOrm.context_id == context_id,
                )
                .order_by(asc(ChunkOrm.chunk_index))
                .all()
            )
        return [self._to_model(o) for o in rows]

    def delete_by_document(self, document_id: int) -> None:
        with Session() as db:
            db.query(ChunkOrm).filter(ChunkOrm.document_id == document_id).delete()
            db.commit()
