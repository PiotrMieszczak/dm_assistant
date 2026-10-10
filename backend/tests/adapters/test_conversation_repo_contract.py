"""One suite, every ConversationRepo. If both pass, swapping them changes nothing."""

from datetime import UTC, datetime, timedelta

import pytest
from app.adapters.persistence.sqlalchemy.engine import create_session_factory
from app.adapters.persistence.sqlalchemy.repositories import SqlConversationRepo
from app.domain.assistant import Conversation, Message, Mode, Role
from app.domain.shared import NotFound
from app.ports.repositories import ConversationRepo

T0 = datetime(2026, 10, 10, 18, 0, tzinfo=UTC)


def _conversation(repo: ConversationRepo, campaign_id: str = "ashfall") -> Conversation:
    conversation = Conversation(
        id=repo.next_conversation_id(),
        campaign_id=campaign_id,
        mode=Mode.RESEARCH,
        started_at=T0,
    )
    repo.save(conversation)
    return conversation


def _message(
    repo: ConversationRepo, conversation: Conversation, role: Role, content: str
) -> Message:
    message = Message(
        id=repo.next_message_id(),
        conversation_id=conversation.id,
        role=role,
        content=content,
        created_at=T0 + timedelta(seconds=1),
        mode=conversation.mode,
    )
    repo.add_message(message)
    return message


def test_ids_are_unique(conversation_repo: ConversationRepo) -> None:
    assert conversation_repo.next_message_id() != conversation_repo.next_message_id()
    assert (
        conversation_repo.next_conversation_id()
        != conversation_repo.next_conversation_id()
    )


def test_saved_conversation_reads_back(conversation_repo: ConversationRepo) -> None:
    saved = _conversation(conversation_repo)
    loaded = conversation_repo.get(saved.id)
    assert loaded == saved


def test_messages_read_back_in_order_with_mode(
    conversation_repo: ConversationRepo,
) -> None:
    conversation = _conversation(conversation_repo)
    asked = _message(conversation_repo, conversation, Role.USER, "Who is Doran Vey?")
    answered = _message(
        conversation_repo, conversation, Role.ASSISTANT, "Not in your material."
    )

    loaded = conversation_repo.get(conversation.id)
    assert loaded is not None
    assert loaded.messages == [asked, answered]
    assert all(message.mode is Mode.RESEARCH for message in loaded.messages)


def test_unknown_conversation_is_none(conversation_repo: ConversationRepo) -> None:
    assert conversation_repo.get(424242) is None


def test_list_is_scoped_to_campaign(conversation_repo: ConversationRepo) -> None:
    """BND-003: another campaign's conversations are never returned."""
    mine = _conversation(conversation_repo, "ashfall")
    _conversation(conversation_repo, "other")
    assert [c.id for c in conversation_repo.list_for_campaign("ashfall")] == [mine.id]


def test_unknown_campaign_is_not_found(conversation_repo: ConversationRepo) -> None:
    with pytest.raises(NotFound):
        _conversation(conversation_repo, "no-such-campaign")


def test_message_for_unknown_conversation_is_not_found(
    conversation_repo: ConversationRepo,
) -> None:
    ghost = Conversation(
        id=424242, campaign_id="ashfall", mode=Mode.RESEARCH, started_at=T0
    )
    with pytest.raises(NotFound):
        _message(conversation_repo, ghost, Role.USER, "hello")


def test_conversation_survives_a_new_process(sessions, migrated: str) -> None:
    """AC-005 pattern: a second engine, like a restarted backend, sees prior writes."""
    first = SqlConversationRepo(sessions)
    conversation = _conversation(first)
    _message(first, conversation, Role.USER, "Still here?")

    restarted = SqlConversationRepo(create_session_factory(migrated))
    loaded = restarted.get(conversation.id)
    assert loaded is not None
    assert [m.content for m in loaded.messages] == ["Still here?"]
