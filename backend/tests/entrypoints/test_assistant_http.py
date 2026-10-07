import json

from fastapi.testclient import TestClient


def _events(body: str) -> list[tuple[str, dict]]:
    parsed: list[tuple[str, dict]] = []
    for block in body.strip().split("\n\n"):
        if not block:
            continue
        name = ""
        data = ""
        for line in block.split("\n"):
            if line.startswith("event:"):
                name = line.removeprefix("event:").strip()
            elif line.startswith("data:"):
                data = line.removeprefix("data:").strip()
        parsed.append((name, json.loads(data)))
    return parsed


def test_create_conversation_and_stream_a_research_turn(client: TestClient) -> None:
    created = client.post("/api/v1/campaigns/ashfall/conversations", json={"mode": "research"})
    assert created.status_code == 201
    payload = created.json()
    assert payload["mode"] == "research"
    assert payload["campaignId"] == "ashfall"
    conversation_id = payload["id"]

    streamed = client.post(
        f"/api/v1/campaigns/ashfall/conversations/{conversation_id}/messages",
        json={"content": "What did we establish about Doran Vey?"},
    )
    assert streamed.status_code == 200
    assert streamed.headers["content-type"].startswith("text/event-stream")

    names = [name for name, _ in _events(streamed.text)]
    assert names[0] == "RunStarted"
    assert names[1] == "TextMessageStart"
    assert "TextMessageContent" in names
    assert names[-2] == "TextMessageEnd"
    assert names[-1] == "RunFinished"

    history = client.get(f"/api/v1/campaigns/ashfall/conversations/{conversation_id}/messages")
    assert history.status_code == 200
    messages = history.json()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
    assert messages[0]["mode"] == "research"
    assert messages[1]["mode"] == "research"


def test_wrong_campaign_is_404(client: TestClient) -> None:
    created = client.post("/api/v1/campaigns/ashfall/conversations", json={})
    conversation_id = created.json()["id"]
    missing = client.get(f"/api/v1/campaigns/other/conversations/{conversation_id}/messages")
    assert missing.status_code == 404
    assert missing.json() == {"detail": "conversation not found"}
