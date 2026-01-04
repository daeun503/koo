from app.repositories.chunk import ChunkRepository
from app.repositories.document import DocumentRepository
from app.repositories.ingestor import Ingestor
from app.repositories.llm import Embedder
from app.repositories.query_log import QueryLogRepository
from app.repositories.vector_store import VectorStoreRepository


class IngestService:
    def __init__(
        self,
        *,
        chunk_repo: ChunkRepository,
        document_repo: DocumentRepository,
        query_log_repo: QueryLogRepository,
        vector_store_repo: VectorStoreRepository,
        embedder: Embedder,
    ):
        self.chunk_repo = chunk_repo
        self.document_repo = document_repo
        self.query_log_repo = query_log_repo
        self.vector_store_repo = vector_store_repo
        self.embedder = embedder

    def ingest(self, ingestor: Ingestor) -> dict:
        doc = ingestor.build_document()
        document = self.document_repo.upsert(
            domain=doc.domain,
            source_type=doc.source_type,
            source_id=doc.source_id,
            title=doc.title,
            raw_content=doc.raw_content,
        )
        if document and document.id:
            self.chunk_repo.delete_by_document(document_id=document.id)

        chunks = ingestor.get_chunks(doc)
        chunks = self.chunk_repo.bulk_create(document_id=document.id, chunks=chunks)

        texts = [c.chunk_text for c in chunks]
        embeddings = self.embedder.embed_documents(texts)

        self.vector_store_repo.bulk_upsert(
            domain=doc.domain,
            source_type=doc.source_type,
            chunk_ids=[c.id for c in chunks],
            embeddings=embeddings,
        )

        return {"document_id": document.id, "chunks": chunks}
