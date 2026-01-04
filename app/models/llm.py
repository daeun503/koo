from pydantic import BaseModel, Field


class Output(BaseModel):
    answer: str = Field(..., description="Final answer for the user")
    sources: list[int] = Field(default_factory=list, description="Used context indices (1-based), e.g. [1,3]")
    confidence: float = Field(0.0, description="0~1 rough confidence based on context sufficiency")

    def to_pretty_text(self):
        used = ", ".join(str(i) for i in self.sources) if self.sources else "none"
        return f"{self.answer}\n\n(sources: {used}, confidence: {self.confidence:.2f})"


class RAGPrompt(BaseModel):
    system: str = Field(
        ...,
        description="System prompt applied to the agent",
        min_length=1,
    )
    user: str = Field(
        ...,
        description="User prompt template. Use {question}, {context} placeholders.",
        min_length=1,
    )

    class Config:
        frozen = True
        extra = "forbid"

    def render(self, *, question: str, context: str) -> str:
        try:
            return self.user.format(
                question=question,
                context=context,
            )
        except KeyError as e:
            raise ValueError(f"Prompt template missing placeholder: {e}") from e

    @classmethod
    def default(cls) -> "RAGPrompt":
        return cls(
            system=(
                "You are koo, a personal assistant.\n"
                "Answer using ONLY the provided context.\n"
                "If context is insufficient, say you don't know and ask a clarifying question.\n"
                "Return JSON matching the output schema.\n"
            ),
            user=(
                "Question:\n{question}\n\n"
                "Context:\n{context}\n\n"
                "Instructions:\n"
                "- Write a concise, actionable answer.\n"
                "- If you used any context items, include their indices in `sources`.\n"
                "- Set `confidence` between 0 and 1.\n"
            ),
        )
