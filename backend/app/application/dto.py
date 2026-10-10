from dataclasses import dataclass
from datetime import datetime

from app.domain.assistant import Mode, Role


@dataclass(frozen=True)
class ConversationView:
    id: int
    campaign_id: str
    mode: Mode
    started_at: datetime


@dataclass(frozen=True)
class MessageView:
    id: int
    role: Role
    content: str
    created_at: datetime
    mode: Mode
    tool_label: str | None


@dataclass(frozen=True)
class TurnStarted:
    conversation_id: int
    run_id: str
    message_id: int


@dataclass(frozen=True)
class TurnDelta:
    message_id: int
    text: str


@dataclass(frozen=True)
class TurnFinished:
    conversation_id: int
    run_id: str
    message_id: int


TurnEvent = TurnStarted | TurnDelta | TurnFinished
