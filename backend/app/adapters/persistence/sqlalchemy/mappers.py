"""Row <-> entity translation. The domain never sees a row."""

from app.adapters.persistence.sqlalchemy.tables import ConversationRow, MessageRow
from app.domain.assistant import Conversation, Message, Mode, Role


def message_to_row(message: Message) -> MessageRow:
    return MessageRow(
        id=message.id,
        conversation_id=message.conversation_id,
        role=message.role.value,
        content=message.content,
        mode=message.mode.value,
        tool_label=message.tool_label,
        created_at=message.created_at,
    )


def message_from_row(row: MessageRow) -> Message:
    return Message(
        id=row.id,
        conversation_id=row.conversation_id,
        role=Role(row.role),
        content=row.content,
        created_at=row.created_at,
        mode=Mode(row.mode),
        tool_label=row.tool_label,
    )


def conversation_to_row(conversation: Conversation) -> ConversationRow:
    return ConversationRow(
        id=conversation.id,
        campaign_id=conversation.campaign_id,
        mode=conversation.mode.value,
        started_at=conversation.started_at,
        messages=[message_to_row(message) for message in conversation.messages],
    )


def conversation_from_row(row: ConversationRow) -> Conversation:
    return Conversation(
        id=row.id,
        campaign_id=row.campaign_id,
        mode=Mode(row.mode),
        started_at=row.started_at,
        messages=[message_from_row(message) for message in row.messages],
    )
