from collections.abc import Iterator
from uuid import uuid4

from app.application.dto import TurnDelta, TurnEvent, TurnFinished, TurnStarted
from app.domain.assistant import Message, Role
from app.domain.shared import NotFound, ValidationFailed
from app.ports.clock import Clock
from app.ports.llm import LLMProvider
from app.ports.repositories import ConversationRepo


class RunAssistantTurn:
    def __init__(self, repo: ConversationRepo, llm: LLMProvider, clock: Clock) -> None:
        self._repo = repo
        self._llm = llm
        self._clock = clock

    def execute(
        self, *, campaign_id: str, conversation_id: int, content: str
    ) -> Iterator[TurnEvent]:
        text = content.strip()
        if not text:
            raise ValidationFailed("content is required")

        conversation = self._repo.get(conversation_id)
        if conversation is None or conversation.campaign_id != campaign_id:
            raise NotFound("conversation not found")

        user = Message(
            id=self._repo.next_message_id(),
            conversation_id=conversation.id,
            role=Role.USER,
            content=text,
            created_at=self._clock.now(),
            mode=conversation.mode,
        )
        self._repo.add_message(user)

        assistant_id = self._repo.next_message_id()
        run_id = uuid4().hex
        yield TurnStarted(
            conversation_id=conversation.id,
            run_id=run_id,
            message_id=assistant_id,
        )

        chunks: list[str] = []
        history = self._repo.get(conversation.id)
        if history is None:
            raise NotFound("conversation not found")
        deltas = self._llm.stream(mode=conversation.mode, messages=history.messages)
        for delta in deltas:
            chunks.append(delta)
            yield TurnDelta(message_id=assistant_id, text=delta)

        self._repo.add_message(
            Message(
                id=assistant_id,
                conversation_id=conversation.id,
                role=Role.ASSISTANT,
                content="".join(chunks),
                created_at=self._clock.now(),
                mode=conversation.mode,
            )
        )
        yield TurnFinished(
            conversation_id=conversation.id,
            run_id=run_id,
            message_id=assistant_id,
        )
