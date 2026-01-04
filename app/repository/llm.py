from abc import ABC, abstractmethod


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
    def answer(self, question: str, contexts: list[dict]) -> str: ...

    def _build_context(self, contexts: list[dict], max_chars: int = 6000) -> str:
        parts: list[str] = []
        total = 0
        for i, c in enumerate(contexts, start=1):
            meta = c.get("meta") or {}
            header = f"[{i}] chunk_id={c['chunk_id']} score={c['score']:.4f} source_id={meta.get('source_id')!r} title={meta.get('title')!r}"
            body = (c.get("chunk_text") or "").strip()
            block = f"{header}\n{body}\n"
            if total + len(block) > max_chars:
                break
            parts.append(block)
            total += len(block)
        return "\n".join(parts)
