from app.enums import Domain, SourceType
from app.models.base import Document as DocumentModel
from app.repository.document import DocumentRepository
from app.utils import compute_content_hash
from infra.db.base import Session
from infra.db.orm.base import Document as DocumentOrm


class DocumentRepositoryImpl(DocumentRepository):
    @staticmethod
    def _to_model(o: DocumentOrm) -> DocumentModel:
        return DocumentModel(
            id=o.id,
            domain=o.domain,
            source_type=o.source_type,
            source_id=o.source_id,
            title=o.title,
            raw_content=o.raw_content,
            content_hash=o.content_hash,
            version=o.version,
        )

    def create(
        self,
        domain: Domain,
        source_type: SourceType,
        source_id: str,
        title: str | None,
        raw_content: str,
    ) -> DocumentModel:
        o = DocumentOrm(
            domain=domain,
            source_type=source_type,
            source_id=source_id,
            title=title,
            raw_content=raw_content,
            content_hash=compute_content_hash(raw_content),
            version=1,
        )

        with Session() as db:
            db.add(o)
            db.commit()
            db.refresh(o)
            return self._to_model(o)

    def get(self, id: int) -> DocumentModel | None:
        with Session() as db:
            o = (
                db.query(DocumentOrm)
                .filter(
                    DocumentOrm.id == id,
                    DocumentOrm.deleted_at.is_(None),
                )
                .one_or_none()
            )
            return self._to_model(o) if o else None

    def get_by_source(
        self,
        source_type: SourceType,
        source_id: str,
    ) -> DocumentModel | None:
        with Session() as db:
            o = (
                db.query(DocumentOrm)
                .filter(
                    DocumentOrm.source_type == source_type,
                    DocumentOrm.source_id == source_id,
                    DocumentOrm.deleted_at.is_(None),
                )
                .one_or_none()
            )
            return self._to_model(o) if o else None

    def all(
        self,
        domain: Domain | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[DocumentModel]:
        with Session() as db:
            q = db.query(DocumentOrm).filter(DocumentOrm.deleted_at.is_(None))
            if domain is not None:
                q = q.filter(DocumentOrm.domain == domain)

            rows = q.order_by(DocumentOrm.id.desc()).offset(offset).limit(limit).all()
            return [self._to_model(o) for o in rows]

    def update(self, document: DocumentModel) -> DocumentModel:
        if document.id is None:
            raise ValueError("document.id is required for update()")

        with Session() as db:
            o = (
                db.query(DocumentOrm)
                .filter(
                    DocumentOrm.id == document.id,
                    DocumentOrm.deleted_at.is_(None),
                )
                .one_or_none()
            )
            if o is None:
                raise KeyError(f"Document not found: id={document.id}")

            o.domain = document.domain
            o.source_type = document.source_type
            o.source_id = document.source_id
            o.title = document.title
            o.raw_content = document.raw_content
            o.content_hash = document.content_hash
            o.version = document.version

            db.add(o)
            db.commit()
            db.refresh(o)
            return self._to_model(o)

    def upsert(
        self,
        domain: Domain,
        source_type: SourceType,
        source_id: str,
        title: str | None,
        raw_content: str,
    ) -> DocumentModel:
        new_hash = compute_content_hash(raw_content)

        with Session() as db:
            o = (
                db.query(DocumentOrm)
                .filter(
                    DocumentOrm.source_type == source_type,
                    DocumentOrm.source_id == source_id,
                    DocumentOrm.deleted_at.is_(None),
                )
                .one_or_none()
            )

            if o is None:
                o = DocumentOrm(
                    domain=domain,
                    source_type=source_type,
                    source_id=source_id,
                    title=title,
                    raw_content=raw_content,
                    content_hash=new_hash,
                    version=1,
                )
                db.add(o)
                db.commit()
                db.refresh(o)
                return self._to_model(o)

            if o.content_hash == new_hash:
                return self._to_model(o)

            o.title = title
            o.raw_content = raw_content
            o.content_hash = new_hash
            o.version = (o.version or 0) + 1

            db.add(o)
            db.commit()
            db.refresh(o)
            return self._to_model(o)

    def delete(self, id: int) -> None:
        with Session() as db:
            o = (
                db.query(DocumentOrm)
                .filter(
                    DocumentOrm.id == id,
                    DocumentOrm.deleted_at.is_(None),
                )
                .one_or_none()
            )
            if o is None:
                return

            o.soft_delete()
            db.add(o)
            db.commit()
