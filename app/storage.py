"""Feedback/state adapters with a deterministic local default and Firestore path."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol


class FeedbackStore(Protocol):
    def record(self, session_id: str, feedback: str) -> dict[str, str]: ...


@dataclass
class InMemoryFeedbackStore:
    entries: list[dict[str, str]] = field(default_factory=list)

    def record(self, session_id: str, feedback: str) -> dict[str, str]:
        item = {
            "session_id": session_id,
            "feedback": feedback,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "store": "memory",
        }
        self.entries.append(item)
        return item


class FirestoreFeedbackStore:
    """Firestore-backed feedback store.

    Construction is lazy so deterministic tests do not require Google Cloud
    credentials. Setting INTENTGUARD_STORAGE=firestore opts into this adapter.
    """

    def __init__(self, project: str | None = None) -> None:
        from google.cloud import firestore

        self._db = firestore.Client(project=project or None)

    def record(self, session_id: str, feedback: str) -> dict[str, str]:
        item = {
            "session_id": session_id,
            "feedback": feedback,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "store": "firestore",
        }
        self._db.collection("intentguard_feedback").document().set(item)
        return item


_MEMORY_STORE = InMemoryFeedbackStore()


def get_feedback_store() -> FeedbackStore:
    storage = os.getenv("INTENTGUARD_STORAGE", "memory").strip().lower()
    if storage == "firestore":
        return FirestoreFeedbackStore(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
    if storage != "memory":
        raise ValueError("INTENTGUARD_STORAGE must be 'memory' or 'firestore'")
    return _MEMORY_STORE


def record_feedback(session_id: str, feedback: str) -> dict[str, str]:
    """Record explicit user feedback using the configured storage adapter."""

    if not session_id.strip():
        raise ValueError("session_id is required")
    if not feedback.strip():
        raise ValueError("feedback is required")
    return get_feedback_store().record(session_id.strip(), feedback.strip())
