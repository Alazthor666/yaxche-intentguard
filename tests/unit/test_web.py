from fastapi.testclient import TestClient

from app.web import web_app


client = TestClient(web_app)


def test_judge_demo_page_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "YAXCHÉ IntentGuard" in response.text
    assert "Collaborative Partner" in response.text


def test_healthz_is_explicit_about_runtime():
    response = client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "yaxche-intentguard"
    assert body["model"] == "gemini-3.7-flash"


def test_ambiguous_request_stops_before_model():
    response = client.post(
        "/api/intent",
        json={"request": "I need to send an important report today. Help me do it."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["phase"] == "clarification"
    assert body["model_called"] is False
    assert body["boundary"] == "deterministic_pre_model"
    assert body["intent_ir"]["material_ambiguity"] is True
    assert body["intent_ir"]["status"] == "CLARIFY_BEFORE_EXECUTION"
    assert "recipient" in body["intent_ir"]["unknowns"]


def test_feedback_route_uses_configured_adapter(monkeypatch):
    def fake_record(session_id: str, feedback: str) -> dict[str, str]:
        return {"session_id": session_id, "feedback": feedback, "store": "test"}

    monkeypatch.setattr("app.web.record_feedback", fake_record)
    response = client.post(
        "/api/feedback",
        json={"session_id": "judge-session", "feedback": "Ask one question at a time."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["saved"] is True
    assert body["record"]["store"] == "test"
