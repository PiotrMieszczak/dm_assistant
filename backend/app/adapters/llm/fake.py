from collections.abc import Iterator, Sequence

from app.adapters.llm.prompts.research import RESEARCH_PROMPT
from app.domain.assistant import Message, Mode

_SCRIPTED = (
    "This is a scripted Research reply. Indexed material is not searched yet, "
    "so I cannot ground an answer in your books."
)


class FakeLLM:
    """Deterministic Gateway adapter. No network, no SDK."""

    def stream(self, *, mode: Mode, messages: Sequence[Message]) -> Iterator[str]:
        del messages
        if mode is not Mode.RESEARCH:
            raise ValueError("fake LLM only serves research mode")
        # The prompt is selected here so grounding stays inside the Gateway.
        _ = RESEARCH_PROMPT
        for word in _SCRIPTED.split(" "):
            yield f"{word} " if not word.endswith(".") else word
