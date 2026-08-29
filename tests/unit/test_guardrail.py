"""The guardrail is what makes this reusable rather than an app.

These tests cover the parts that hold without ADK installed, plus the one
refusal that matters most: never silently replacing somebody else's safety hook.
"""

from __future__ import annotations

import json

import pytest

from app.guardrail import (
    GATE_MARKER,
    compile_boundary,
    gate_message,
    install_intent_boundary,
    latest_user_text,
)


class _Part:
    def __init__(self, text: str | None) -> None:
        self.text = text


class _Content:
    def __init__(self, role: str, texts: list[str | None]) -> None:
        self.role = role
        self.parts = [_Part(t) for t in texts]


class _Request:
    def __init__(self, contents: list[_Content] | None) -> None:
        self.contents = contents


class _Agent:
    def __init__(self, before_model_callback=None) -> None:
        self.before_model_callback = before_model_callback


def test_compile_boundary_is_the_same_decision_as_the_core():
    assert compile_boundary("Do it").material_ambiguity is True
    assert compile_boundary("Write a haiku about the sea").material_ambiguity is False


def test_gate_message_carries_marker_question_and_parsable_ir():
    intent = compile_boundary("Send the report")
    message = gate_message(intent)

    assert message.startswith(GATE_MARKER)
    assert "QUESTION=Who should receive it?" in message

    payload = message.split("INTENT_IR_JSON=", 1)[1].split("\nQUESTION=", 1)[0]
    parsed = json.loads(payload)
    assert parsed["status"] == "CLARIFY_BEFORE_EXECUTION"
    assert "recipient" in parsed["unknowns"]


def test_latest_user_text_takes_the_most_recent_user_turn():
    request = _Request([
        _Content("user", ["first"]),
        _Content("model", ["ignored"]),
        _Content("user", ["second"]),
    ])
    assert latest_user_text(request) == "second"


def test_latest_user_text_skips_empty_parts():
    request = _Request([_Content("user", [None, "", "real"])])
    assert latest_user_text(request) == "real"


def test_latest_user_text_returns_none_without_user_turns():
    assert latest_user_text(_Request([])) is None
    assert latest_user_text(_Request(None)) is None
    assert latest_user_text(_Request([_Content("model", ["only model"])])) is None


def test_install_refuses_to_replace_an_existing_callback():
    """Silently overwriting another team's safety hook is the same class of
    mistake this project exists to prevent."""
    def somebody_elses_guard(ctx, req):  # pragma: no cover - never invoked
        return None

    agent = _Agent(before_model_callback=somebody_elses_guard)
    with pytest.raises(ValueError, match="AGENT_ALREADY_HAS_BEFORE_MODEL_CALLBACK"):
        install_intent_boundary(agent)

    assert agent.before_model_callback is somebody_elses_guard
