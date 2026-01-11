import asyncio

from pydantic_ai import Agent, Embedder, RunUsage
from pydantic_ai.embeddings import EmbeddingSettings

from app.models.base import VectorSearchChunk
from app.models.llm import Output, RAGPrompt
from app.repositories.llm import Answerer as AnswererRepository
from app.repositories.llm import Embedder as EmbedderRepository
from config import settings


class OpenaiEmbedder(EmbedderRepository):
    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set")

        self._dim = settings.EMBEDDING_DIM

        emb_settings = EmbeddingSettings(dimensions=self._dim) if self._dim else None
        self._embedder = Embedder(settings.EMBEDDING_MODEL, settings=emb_settings)

    @property
    def dim(self) -> int:
        return self._dim

    def embed_query(self, text: str) -> list[float]:
        async def _run() -> list[float]:
            result = await self._embedder.embed_query(text)
            return list(result.embeddings[0])

        return asyncio.run(_run())

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        async def _run() -> list[list[float]]:
            result = await self._embedder.embed_documents(texts)
            return [list(v) for v in result.embeddings]

        return asyncio.run(_run())


class OpenaiAnswerer(AnswererRepository):
    def __init__(self, prompt: RAGPrompt | None = None) -> None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set")

        self._prompt = prompt or RAGPrompt.default()
        self._agent = Agent(
            settings.LLM_MODEL,
            output_type=Output,
            system_prompt=self._prompt.system,
        )

    def answer(self, question: str, contexts: list[VectorSearchChunk]) -> tuple[Output, RunUsage]:
        ctx = self._build_context(contexts)
        prompt = self._prompt.render(question=question, context=ctx)

        result = self._agent.run_sync(prompt)
        return result.output, result.usage()

    def summarize_image(self, image: bytes | str) -> str:
        """
        이미지를 한국어로 1~2문장으로 요약해줘.

        핵심 키워드, 주제, 등장하는 개체명(사람/장소/제품 등)과 중요한 텍스트(표지, 간판, 인쇄물 등)가 있으면 포함해줘.
        요약 내용은 나중에 벡터서치로 검색될 때 최대한 의미있게 해줘.
        """
        from pydantic_ai import BinaryContent, ImageUrl
        import base64

        agent = Agent(
            settings.LLM_MODEL,
            system_prompt="당신은 이미지에서 텍스트를 정확하게 추출하는 전문가입니다.",
        )

        if isinstance(image, str) and image.startswith(("http://", "https://")):
            result = agent.run_sync(
                [
                    "이미지를 한국어로 1~2문장으로 요약해줘. "
                    "핵심 키워드, 주제, 등장하는 개체명(사람/장소/제품 등)과 중요한 텍스트(표지, 간판, 인쇄물 등)가 있으면 포함해줘. "
                    "요약 내용은 나중에 벡터서치로 검색될 때 최대한 의미있게 해줘.",
                    ImageUrl(url=image),
                ]
            )
        else:
            if isinstance(image, str):
                image_bytes = base64.b64decode(image)
            else:
                image_bytes = image

            result = agent.run_sync(
                [
                    "이미지를 한국어로 1~2문장으로 요약해줘. "
                    "핵심 키워드, 주제, 등장하는 개체명(사람/장소/제품 등)과 중요한 텍스트(표지, 간판, 인쇄물 등)가 있으면 포함해줘. "
                    "요약 내용은 나중에 벡터서치로 검색될 때 최대한 의미있게 해줘.",
                    BinaryContent(data=image_bytes, media_type="image/jpeg"),
                ]
            )

        return result.output
