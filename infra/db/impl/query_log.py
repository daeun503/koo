from app.enums import RouterDomain
from app.models.base import QueryLog as QueryLogModel
from app.repository.query_log import QueryLogRepository
from infra.db.base import Session
from infra.db.orm.base import QueryLog as QueryLogOrm


class QueryLogRepositoryImpl(QueryLogRepository):
    @staticmethod
    def _to_model(o: QueryLogOrm) -> QueryLogModel:
        return QueryLogModel(
            id=o.id,
            query_text=o.query_text,
            router_domain=o.router_domain,
            topk=o.topk,
            selected_chunk_ids=o.selected_chunk_ids,
            answer=o.answer,
        )

    def create(
        self,
        query_text: str,
        router_domain: RouterDomain,
        topk: int,
        selected_chunk_ids: list[int] | None = None,
        answer: str | None = None,
    ) -> QueryLogModel:
        o = QueryLogOrm(
            query_text=query_text,
            router_domain=router_domain,
            topk=topk,
            selected_chunk_ids=selected_chunk_ids,
            answer=answer,
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

    def all(self, limit: int = 100, offset: int = 0) -> list[QueryLogModel]:
        with Session() as db:
            rows = db.query(QueryLogOrm).order_by(QueryLogOrm.id.desc()).offset(offset).limit(limit).all()
            return [self._to_model(o) for o in rows]

    def update(
        self,
        id: int,
        query_text: str | None,
        router_domain: RouterDomain | None,
        topk: int | None,
        selected_chunk_ids: list[int] | None = None,
        answer: str | None = None,
    ) -> QueryLogModel:
        with Session() as db:
            o: QueryLogOrm = db.query(QueryLogOrm).filter(QueryLogOrm.id == id).one_or_none()
            if o is None:
                raise KeyError(f"QueryLog not found: id={id}")

            o.query_text = query_text or o.query_text
            o.router_domain = router_domain or o.router_domain
            o.topk = topk or o.topk
            o.selected_chunk_ids = selected_chunk_ids or o.selected_chunk_ids
            o.answer = answer or o.answer

            db.add(o)
            db.commit()
            db.refresh(o)
            return self._to_model(o)

    def delete(self, id: int) -> None:
        with Session() as db:
            db.query(QueryLogOrm).filter(QueryLogOrm.id == id).delete()
            db.commit()
