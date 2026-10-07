from collections.abc import Iterator, Sequence
from typing import Protocol

from app.domain.assistant import Message, Mode


class LLMProvider(Protocol):
    """The Gateway boundary (BND-002, ADR-0006). Adapters live in app.adapters.llm."""

    def stream(self, *, mode: Mode, messages: Sequence[Message]) -> Iterator[str]:
        """Yield text deltas. Prompting and grounding belong to the adapter."""
        ...
