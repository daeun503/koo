from typing import Sequence

import httpx
from pydantic_ai import Agent, RunUsage
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider

from app.models.base import VectorSearchChunk
from app.models.llm import Output, RAGPrompt
from app.repositories.llm import Answerer as AnswererRepository
from app.repositories.llm import Embedder as EmbedderRepository
from config import settings


class OllamaEmbedder(EmbedderRepository):
    def __init__(self) -> None:
        self._base_url: str = settings.OLLAMA_BASE_URL
        self._model: str = settings.EMBEDDING_MODEL
        self._dim = settings.EMBEDDING_DIM
        self._client = httpx.Client(base_url=self._base_url, timeout=60)

    def _probe_dim(self) -> int:
        vec = self._embed_one("dimension probe")
        if not vec:
            raise RuntimeError("Failed to probe embedding dimension from Ollama.")
        return len(vec)

    def _parse_embeddings(self, data: dict) -> list[list[float]]:
        if "embeddings" in data and isinstance(data["embeddings"], list):
            return [[float(x) for x in row] for row in data["embeddings"]]

        if "embedding" in data and isinstance(data["embedding"], list):
            return [[float(x) for x in data["embedding"]]]

        raise RuntimeError(f"Unexpected Ollama embedding response shape: keys={list(data.keys())}")

    def _embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        url = "/api/embed"
        payload = {
            "model": self._model,
            "input": list(texts) if len(texts) > 1 else texts[0],
        }

        resp = self._client.post(url, json=payload)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Ollama embedding request failed: {e.response.text}") from e

        data = resp.json()
        vectors = self._parse_embeddings(data)
        return vectors

    def _embed_one(self, text: str) -> list[float]:
        vecs = self._embed_batch([text])
        return vecs[0] if vecs else []

    @property
    def dim(self) -> int:
        if self._dim is None:
            self._dim = self._probe_dim()
        return self._dim

    def embed_query(self, text: str) -> list[float]:
        return self._embed_one(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._embed_batch(texts)


class OllamaAnswerer(AnswererRepository):
    def __init__(self, prompt: RAGPrompt | None = None) -> None:
        model = OpenAIChatModel(
            model_name=settings.LLM_MODEL,
            provider=OllamaProvider(base_url=f"{settings.OLLAMA_BASE_URL}/v1", api_key=settings.OLLAMA_API_KEY),
        )

        self._prompt = prompt or RAGPrompt.default()
        self._agent = Agent(
            model,
            output_type=Output,
            system_prompt=self._prompt.system,
        )

    def answer(self, question: str, contexts: list[VectorSearchChunk]) -> tuple[Output, RunUsage]:
        ctx = self._build_context(contexts)
        prompt = self._prompt.render(question=question, context=ctx)

        result = self._agent.run_sync(prompt)
        return result.output, result.usage()
