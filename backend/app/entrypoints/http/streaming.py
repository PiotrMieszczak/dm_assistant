import json

from app.application.dto import TurnDelta, TurnEvent, TurnFinished, TurnStarted


def sse(event: str, data: dict[str, object]) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def ag_ui_frame(event: TurnEvent) -> str:
    """Map turn events to AG-UI (ADR-0009). Protocol stays out of the loop."""
    if isinstance(event, TurnStarted):
        started = sse(
            "RunStarted",
            {"threadId": str(event.conversation_id), "runId": event.run_id},
        )
        message_start = sse(
            "TextMessageStart",
            {"messageId": str(event.message_id), "role": "assistant"},
        )
        return started + message_start
    if isinstance(event, TurnDelta):
        return sse(
            "TextMessageContent",
            {"messageId": str(event.message_id), "delta": event.text},
        )
    if isinstance(event, TurnFinished):
        return sse("TextMessageEnd", {"messageId": str(event.message_id)}) + sse(
            "RunFinished",
            {
                "threadId": str(event.conversation_id),
                "runId": event.run_id,
                "outcome": "success",
            },
        )
    raise TypeError(f"unknown turn event: {type(event)!r}")
