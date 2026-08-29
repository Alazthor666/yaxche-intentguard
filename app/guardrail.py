"""Install the IntentGuard boundary on any Google ADK agent.

Most attempts to make an agent cautious are written as instructions: *ask before
you act, do not assume the recipient, check authorization first*. An instruction
is a request to a probabilistic system. It holds most of the time, which is
another way of saying it fails some of the time, and the failures arrive exactly
when the request is unusual enough to matter.

This boundary is not an instruction. It is an ADK `before_model_callback`, so
the framework runs it before the model is invoked at all. A materially ambiguous
request never reaches Gemini, whatever the model might have preferred to do with
it.

    from google.adk.agents import Agent
    from app.guardrail import install_intent_boundary

    agent = Agent(name="my_agent", model=..., instruction=...)
    install_intent_boundary(agent)

Three lines, any ADK agent, no prompt engineering.

```text
INSTRUCTION_IS_A_REQUEST
CALLBACK_IS_A_BOUNDARY
PROMPT_COMPLIANCE != ENFORCEMENT
PLAUSIBLE_INTERPRETATION != AUTHORIZATION
```

The boundary decides one thing only: whether to stop and ask. It never decides
what the answer should be, never grants authority, and never claims an action
happened.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Protocol

from .clarification import compile_intent
from .contracts import IntentIR

GATE_MARKER = "INTENTGUARD_GATE=CLARIFY_BEFORE_EXECUTION"


class SupportsCallbacks(Protocol):
    """The narrow slice of an ADK agent this module touches."""

    before_model_callback: Any


def compile_boundary(request: str) -> IntentIR:
    """Public entry point for callers that want the decision without ADK."""
    return compile_intent(request)


def gate_message(intent: IntentIR) -> str:
    """Render a stop as text an ADK surface can return in place of a model turn."""
    serialized = json.dumps(intent.model_dump(), sort_keys=True)
    return (
        f"{GATE_MARKER}\n"
        f"INTENT_IR_JSON={serialized}\n"
        f"QUESTION={intent.clarification_question}"
    )


def latest_user_text(llm_request: Any) -> str | None:
    """Pull the most recent textual user turn out of an ADK LlmRequest."""
    for content in reversed(getattr(llm_request, "contents", None) or []):
        if getattr(content, "role", None) != "user" or not getattr(content, "parts", None):
            continue
        for part in reversed(content.parts):
            text = getattr(part, "text", None)
            if text:
                return text
    return None


def make_before_model_callback(
    *,
    on_stop: Callable[[IntentIR], None] | None = None,
) -> Callable[[Any, Any], Any]:
    """Build an ADK `before_model_callback` that enforces the intent boundary.

    `on_stop` receives the IntentIR whenever a request is held back, which is the
    hook for evidence recording, metrics, or a UI. It is called for its side
    effect only: returning something from it cannot let a stopped request
    through, because a callback that could be talked out of stopping would not be
    a boundary.
    """
    # Imported lazily so this module is importable, and unit-testable, on a
    # machine that has no ADK installed.
    from google.adk.models.llm_response import LlmResponse
    from google.genai import types

    def before_model_callback(callback_context: Any, llm_request: Any) -> Any:
        del callback_context
        request = latest_user_text(llm_request)
        if request is None:
            return None

        intent = compile_intent(request)
        if not intent.material_ambiguity:
            return None

        if on_stop is not None:
            try:
                on_stop(intent)
            except Exception:  # noqa: BLE001 - observation must never unblock
                pass

        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part.from_text(text=gate_message(intent))],
            )
        )

    return before_model_callback


def install_intent_boundary(
    agent: SupportsCallbacks,
    *,
    on_stop: Callable[[IntentIR], None] | None = None,
) -> SupportsCallbacks:
    """Attach the boundary to an existing ADK agent and return it.

    Refuses to overwrite a callback that is already present. Silently replacing
    another team's safety hook would be the same class of mistake this project
    exists to prevent.
    """
    existing = getattr(agent, "before_model_callback", None)
    if existing is not None:
        raise ValueError(
            "AGENT_ALREADY_HAS_BEFORE_MODEL_CALLBACK: refusing to replace it. "
            "Compose the two explicitly if both are wanted."
        )
    agent.before_model_callback = make_before_model_callback(on_stop=on_stop)
    return agent
