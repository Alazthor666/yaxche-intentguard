import os

from app.storage import InMemoryFeedbackStore, get_feedback_store, record_feedback


def test_memory_store_records_feedback(monkeypatch):
    monkeypatch.setenv("INTENTGUARD_STORAGE", "memory")
    result = record_feedback("session-1", "Ask fewer questions")
    assert result["session_id"] == "session-1"
    assert result["feedback"] == "Ask fewer questions"
    assert result["store"] == "memory"


def test_get_feedback_store_defaults_to_memory(monkeypatch):
    monkeypatch.delenv("INTENTGUARD_STORAGE", raising=False)
    assert isinstance(get_feedback_store(), InMemoryFeedbackStore)


def test_invalid_storage_mode_is_rejected(monkeypatch):
    monkeypatch.setenv("INTENTGUARD_STORAGE", "unknown")
    try:
        get_feedback_store()
    except ValueError as exc:
        assert "memory" in str(exc)
        assert "firestore" in str(exc)
    else:
        raise AssertionError("invalid storage mode must fail closed")
