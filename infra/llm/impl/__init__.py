from app.repositories.llm import Answerer as AnswererRepository
from app.repositories.llm import Embedder as EmbedderRepository

__all__ = [
    "Embedder",
    "Answerer",
]


class Embedder(EmbedderRepository):
    def __init__(self, model: str) -> None:
        if not model:
            raise ValueError("Model must be provided")

        self.model: str = model
        self._impl: EmbedderRepository = self._build_impl(model)

    def _build_impl(self, model: str) -> EmbedderRepository:
        if model == "openai":
            from .openai import OpenaiEmbedder

            return OpenaiEmbedder()
        if model == "ollama":
            from .ollama import OllamaEmbedder

            return OllamaEmbedder()
        raise ValueError(f"Unsupported embedder model: {model}")

    @property
    def dim(self) -> int:
        return self._impl.dim

    def embed_query(self, text: str) -> list[float]:
        return self._impl.embed_query(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._impl.embed_documents(texts)


class Answerer(AnswererRepository):
    def __init__(self, model: str) -> None:
        if not model:
            raise ValueError("Model must be provided")

        self.model: str = model
        self._impl: AnswererRepository = self._build_impl(model)

    def _build_impl(self, model: str) -> AnswererRepository:
        if model == "openai":
            from .openai import OpenaiAnswerer

            return OpenaiAnswerer()
        if model == "ollama":
            from .ollama import OllamaAnswerer

            return OllamaAnswerer()
        raise ValueError(f"Unsupported answerer model: {model}")

    def answer(self, question: str, contexts: list[dict]) -> str:
        return self._impl.answer(question, contexts)
