from dependency_injector import containers, providers

from app.services import AskService, IngestService
from config import settings
from container.ingestor_factory import IngestorFactory
from infra.db.impl import ChunkRepositoryImpl, DocumentRepositoryImpl, QueryLogRepositoryImpl
from infra.llm.impl import Answerer, Embedder
from infra.vector_store.milvus.impl import MilvusRepositoryImpl


class Container(containers.DeclarativeContainer):
    # --- LLM / Embedding ---
    embedder = providers.Singleton(Embedder, model=settings.EMBEDDING_PROVIDER)
    answerer = providers.Singleton(Answerer, model=settings.LLM_PROVIDER)

    # --- Repositories ---
    chunk_repo = providers.Singleton(ChunkRepositoryImpl)
    document_repo = providers.Singleton(DocumentRepositoryImpl)
    query_log_repo = providers.Singleton(QueryLogRepositoryImpl)
    milvus = providers.Singleton(MilvusRepositoryImpl)

    ingestor_factory = providers.Singleton(IngestorFactory)

    # --- Pipeline / Services ---
    ingest_service = providers.Factory(
        IngestService,
        chunk_repo=chunk_repo,
        document_repo=document_repo,
        query_log_repo=query_log_repo,
        vector_store_repo=milvus,
        embedder=embedder,
    )
    ask_service = providers.Factory(
        AskService,
        chunk_repo=chunk_repo,
        query_log_repo=query_log_repo,
        vector_store_repo=milvus,
        embedder=embedder,
        answerer=answerer,
        topk=settings.TOPK,
    )
