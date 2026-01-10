from dependency_injector import containers, providers

from app.services import AskService, IngestService
from config import settings
from container.factory import IngestorFactory, LLMFactory
from infra.db.impl import ChunkRepositoryImpl, DocumentRepositoryImpl, QueryLogRepositoryImpl
from infra.vector_store.milvus.impl import MilvusRepositoryImpl


class Container(containers.DeclarativeContainer):
    # --- Factories ---
    llm_factory = providers.Singleton(LLMFactory)
    ingestor_factory = providers.Singleton(IngestorFactory)

    # --- LLM / Embedding ---
    embedder = providers.Factory(
        lambda factory: factory.create_embedder(settings.EMBEDDING_PROVIDER),
        factory=llm_factory,
    )
    answerer = providers.Factory(
        lambda factory: factory.create_answerer(settings.LLM_PROVIDER),
        factory=llm_factory,
    )

    # --- Repositories ---
    chunk_repo = providers.Singleton(ChunkRepositoryImpl)
    document_repo = providers.Singleton(DocumentRepositoryImpl)
    query_log_repo = providers.Singleton(QueryLogRepositoryImpl)
    milvus = providers.Singleton(MilvusRepositoryImpl)

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
