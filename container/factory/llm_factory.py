from app.repositories.llm import Answerer as AnswererRepository
from app.repositories.llm import Embedder as EmbedderRepository


class LLMFactory:
    def create_embedder(self, provider: str) -> EmbedderRepository:
        match provider:
            case "openai":
                from infra.llm.impl.openai import OpenaiEmbedder

                return OpenaiEmbedder()
            case "ollama":
                from infra.llm.impl.ollama import OllamaEmbedder

                return OllamaEmbedder()
            case _:
                raise ValueError(f"Unsupported embedder provider: {provider}")

    def create_answerer(self, provider: str) -> AnswererRepository:
        match provider:
            case "openai":
                from infra.llm.impl.openai import OpenaiAnswerer

                return OpenaiAnswerer()
            case "ollama":
                from infra.llm.impl.ollama import OllamaAnswerer

                return OllamaAnswerer()
            case _:
                raise ValueError(f"Unsupported answerer provider: {provider}")
