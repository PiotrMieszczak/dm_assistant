from dataclasses import dataclass, field
from datetime import datetime

from app.domain.assistant.values import Mode, Role


@dataclass(frozen=True)
class Message:
    id: int
    conversation_id: int
    role: Role
    content: str
    created_at: datetime
    mode: Mode
    tool_label: str | None = None


@dataclass
class Conversation:
    id: int
    campaign_id: str
    mode: Mode
    started_at: datetime
    messages: list[Message] = field(default_factory=list)
