from dependency_injector import containers, providers

from app.ask.retreiver import Retriever
from app.ingest.pipeline import BaseIngestPipeline
from config import settings

from infra.llm.impl import Embedder, Answerer
from infra.db.impl.chunk import ChunkRepositoryImpl
from infra.db.impl.document import DocumentRepositoryImpl
from infra.db.impl.query_log import QueryLogRepositoryImpl
from infra.vector_store.milvus.impl.milvus import MilvusRepositoryImpl


class Container(containers.DeclarativeContainer):
    # --- LLM / Embedding ---
    embedder = providers.Singleton(Embedder, model=settings.EMBEDDING_PROVIDER)
    answerer = providers.Singleton(Answerer, model=settings.LLM_PROVIDER)

    # --- Repositories ---
    chunk_repo = providers.Singleton(ChunkRepositoryImpl)
    document_repo = providers.Singleton(DocumentRepositoryImpl)
    query_log_repo = providers.Singleton(QueryLogRepositoryImpl)
    milvus = providers.Singleton(MilvusRepositoryImpl)

    # --- Pipeline / Services ---
    ingest_pipeline = providers.Factory(
        BaseIngestPipeline,
        chunk_repo=chunk_repo,
        document_repo=document_repo,
        query_log_repo=query_log_repo,
        vector_store_repo=milvus,
        embedder=embedder,
    )
    retriever = providers.Factory(
        Retriever,
        chunk_repo=chunk_repo,
        vector_store_repo=milvus,
    )
