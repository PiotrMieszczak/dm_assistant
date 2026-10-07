"""The only module that names both sides of a port."""

from dataclasses import dataclass

from fastapi import FastAPI

from app.adapters.clock.system import SystemClock
from app.adapters.llm.fake import FakeLLM
from app.adapters.persistence.memory.conversations import InMemoryConversationRepo
from app.application.assistant import ListMessages, RunAssistantTurn, StartConversation
from app.entrypoints.http.app import create_http_app
from app.ports.clock import Clock
from app.ports.llm import LLMProvider
from app.ports.repositories import ConversationRepo


@dataclass(frozen=True)
class UseCases:
    start_conversation: StartConversation
    run_turn: RunAssistantTurn
    list_messages: ListMessages


def build_use_cases(
    *,
    repo: ConversationRepo | None = None,
    llm: LLMProvider | None = None,
    clock: Clock | None = None,
) -> UseCases:
    conversations = repo or InMemoryConversationRepo()
    provider = llm or FakeLLM()
    time = clock or SystemClock()
    return UseCases(
        start_conversation=StartConversation(conversations, time),
        run_turn=RunAssistantTurn(conversations, provider, time),
        list_messages=ListMessages(conversations),
    )


def build_app(use_cases: UseCases | None = None) -> FastAPI:
    cases = use_cases or build_use_cases()
    app = create_http_app()
    app.state.start_conversation = cases.start_conversation
    app.state.run_turn = cases.run_turn
    app.state.list_messages = cases.list_messages
    return app
