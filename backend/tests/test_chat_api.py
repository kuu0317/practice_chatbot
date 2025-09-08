# チャットAPIのテスト
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 空・長すぎるメッセージのバリデーションテスト
def test_empty_or_long_message():
    r = client.post("/api/chat/ask", json={"message": ""})
    assert r.status_code in (400, 422)
    r = client.post("/api/chat/ask", json={"message": "x" * 201})
    assert r.status_code == 400

# 正常なメッセージでAI応答が返ることをテスト
def test_valid_message_returns_reply(monkeypatch):
    from app.services.ai_client import AIClient
    async def fake_generate_reply(self, message, system):
        return f"[TEST]{message}", 3, 1
    monkeypatch.setattr(AIClient, "generate_reply", fake_generate_reply)

    r = client.post("/api/chat/ask", json={"message": "hi"})
    assert r.status_code == 200
    body = r.json()
    assert body["reply"].startswith("[TEST]")