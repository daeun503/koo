from app.models.base import QueryLog as QueryLogModel
from app.repositories.query_log import QueryLogRepository
from infra.db.base import Session
from infra.db.orm.base import QueryLog as QueryLogOrm


class QueryLogRepositoryImpl(QueryLogRepository):
    @staticmethod
    def _to_model(o: QueryLogOrm) -> QueryLogModel:
        return QueryLogModel(
            id=o.id,
            query_text=o.query_text,
            topk=o.topk,
            selected_chunk_ids=o.selected_chunk_ids,
            expended_chunk_ids=o.expended_chunk_ids,
            answer=o.answer,
        )

    def create(
        self,
        query_text: str,
        topk: int,
    ) -> QueryLogModel:
        o = QueryLogOrm(
            query_text=query_text,
            topk=topk,
        )

        with Session() as db:
            db.add(o)
            db.commit()
            db.refresh(o)
            return self._to_model(o)

    def get(self, id: int) -> QueryLogModel | None:
        with Session() as db:
            o = db.query(QueryLogOrm).filter(QueryLogOrm.id == id).one_or_none()
            return self._to_model(o) if o else None

    def update(
        self,
        id: int,
        selected_chunk_ids: list[int] | None = None,
        expended_chunk_ids: list[int] | None = None,
        answer: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        meta: dict | None = None,
    ) -> QueryLogModel:
        with Session() as db:
            o: QueryLogOrm = db.query(QueryLogOrm).filter(QueryLogOrm.id == id).one_or_none()
            if o is None:
                raise KeyError(f"QueryLog not found: id={id}")

            o.selected_chunk_ids = selected_chunk_ids or o.selected_chunk_ids
            o.expended_chunk_ids = expended_chunk_ids or o.expended_chunk_ids
            o.answer = answer or o.answer
            o.input_tokens = input_tokens or o.input_tokens
            o.output_tokens = output_tokens or o.output_tokens
            o.total_tokens = o.input_tokens + o.output_tokens
            o.meta = meta or o.meta

            db.add(o)
            db.commit()
            db.refresh(o)
            return self._to_model(o)

    def delete(self, id: int) -> None:
        with Session() as db:
            db.query(QueryLogOrm).filter(QueryLogOrm.id == id).delete()
            db.commit()
