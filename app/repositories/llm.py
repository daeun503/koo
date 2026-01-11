from abc import ABC, abstractmethod

from pydantic_ai import RunUsage

from app.models.base import VectorSearchChunk
from app.models.llm import Output


class Embedder(ABC):
    @property
    @abstractmethod
    def dim(self) -> int: ...

    @abstractmethod
    def embed_query(self, text: str) -> list[float]: ...

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...


class Answerer(ABC):
    @abstractmethod
    def answer(self, question: str, contexts: list[VectorSearchChunk]) -> tuple[Output, RunUsage]: ...

    @abstractmethod
    def summarize_image(self, image: bytes | str) -> str: ...

    def _build_context(self, contexts: list[VectorSearchChunk], max_chars: int = 6000) -> str:
        parts: list[str] = []
        total = 0
        for idx, context in enumerate(contexts, start=1):
            header = (
                f"[{idx}] chunk_id={context.chunk_id} score={context.score:.4f} context_id={context.chunk.context_id!r}"
                # f"title={context.chunk.!r}"
            )
            body = context.chunk.chunk_text.strip()

            block = f"{header}\n{body}\n"
            if total + len(block) > max_chars:
                break
            parts.append(block)
            total += len(block)
        return "\n".join(parts)
