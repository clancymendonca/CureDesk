from unittest.mock import MagicMock, patch

from app.config import settings


def test_chat_crisis_short_circuit(client):
    res = client.post("/v1/chat", json={"message": "I have severe chest pain", "history": []})
    assert res.status_code == 200
    assert "emergency" in res.json()["reply"].lower()


def test_chat_offline_fallback_without_groq(client):
    with patch.object(settings, "groq_api_key", ""):
        res = client.post("/v1/chat", json={"message": "what is diabetes", "history": []})
    assert res.status_code == 200
    assert "offline" in res.json()["reply"].lower()


def test_chat_offline_fallback_uses_knowledge_base(client, db_session):
    from app.db.models import KnowledgeChunk

    chunk = KnowledgeChunk(
        source="test",
        question="What is diabetes?",
        answer="Diabetes is a chronic condition affecting blood sugar.",
    )
    db_session.add(chunk)
    db_session.commit()
    try:
        with patch.object(settings, "groq_api_key", ""):
            res = client.post(
                "/v1/chat", json={"message": "tell me about diabetes", "history": []}
            )
        assert res.status_code == 200
        assert "chronic condition" in res.json()["reply"]
    finally:
        db_session.delete(chunk)
        db_session.commit()


def test_chat_with_mocked_groq(client):
    completion = MagicMock()
    completion.choices[0].message.content = "Educational answer only."
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = completion

    with (
        patch.object(settings, "groq_api_key", "test-key"),
        patch("app.routers.chat.Groq", return_value=mock_client),
    ):
        res = client.post(
            "/v1/chat",
            json={
                "message": "what helps a sore throat?",
                "history": [{"role": "user", "content": "hi"}],
            },
        )
    assert res.status_code == 200
    assert res.json()["reply"] == "Educational answer only."
    messages = mock_client.chat.completions.create.call_args.kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert messages[-1] == {"role": "user", "content": "what helps a sore throat?"}
