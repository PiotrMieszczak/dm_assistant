from app.application.dto import ConversationView
from app.domain.assistant import Conversation, Mode
from app.domain.shared import ValidationFailed
from app.ports.clock import Clock
from app.ports.repositories import ConversationRepo


class StartConversation:
    def __init__(self, repo: ConversationRepo, clock: Clock) -> None:
        self._repo = repo
        self._clock = clock

    def execute(self, *, campaign_id: str, mode: Mode) -> ConversationView:
        if mode != Mode.RESEARCH:
            raise ValidationFailed("only research mode is available")
        if not campaign_id.strip():
            raise ValidationFailed("campaign_id is required")

        conversation = Conversation(
            id=self._repo.next_conversation_id(),
            campaign_id=campaign_id,
            mode=mode,
            started_at=self._clock.now(),
        )
        self._repo.save(conversation)
        return ConversationView(
            id=conversation.id,
            campaign_id=conversation.campaign_id,
            mode=conversation.mode,
            started_at=conversation.started_at,
        )
