"""Google ADK root agent for YAXCHÉ IntentGuard."""

from __future__ import annotations

import json
import os

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

from .clarification import compile_intent
from .storage import record_feedback


# Current Google Agents CLI examples use Gemini 3.7 Flash. The hackathon requires
# Gemini 3.5 or newer, so 3.7 satisfies the model floor while keeping the project
# aligned with the current Google agent toolchain.
MODEL = os.getenv("INTENTGUARD_MODEL", "gemini-3.7-flash")


def compile_human_intent(request: str) -> dict:
    """Compile raw human text into a structured IntentIR for transparent inspection."""

    return compile_intent(request).model_dump()


def record_user_feedback(session_id: str, feedback: str) -> dict[str, str]:
    """Persist explicit user feedback through the configured storage adapter."""

    return record_feedback(session_id=session_id, feedback=feedback)


def build_intent_guard_response(request: str) -> LlmResponse | None:
    """Return a blocking ADK response when material ambiguity is present.

    This function is deterministic and runs before model reasoning. Safety and
    intent preservation therefore do not depend on the LLM choosing to call a
    tool or following a prompt instruction probabilistically.
    """

    intent_ir = compile_intent(request)
    if not intent_ir.material_ambiguity:
        return None

    serialized = json.dumps(intent_ir.model_dump(), sort_keys=True)
    message = (
        "INTENTGUARD_GATE=CLARIFY_BEFORE_EXECUTION\n"
        f"INTENT_IR_JSON={serialized}\n"
        f"QUESTION={intent_ir.clarification_question}"
    )
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part.from_text(text=message)],
        )
    )


def _latest_user_text(llm_request: LlmRequest) -> str | None:
    """Extract the latest textual user message from an ADK LLM request."""

    for content in reversed(llm_request.contents or []):
        if content.role != "user" or not content.parts:
            continue
        for part in reversed(content.parts):
            if part.text:
                return part.text
    return None


def intent_boundary_before_model(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> LlmResponse | None:
    """Compile intent before Gemini and short-circuit material ambiguity."""

    del callback_context  # Reserved for future state/evidence recording.
    request = _latest_user_text(llm_request)
    if request is None:
        return None
    return build_intent_guard_response(request)


INSTRUCTION = """
You are YAXCHÉ IntentGuard, a collaborative agent that protects human intent before action.

Runtime invariant:
- Every textual user request is compiled by a deterministic pre-model intent boundary before you are invoked.
- Requests with material ambiguity are stopped before model reasoning and receive the minimum useful clarification question.
- Do not reinterpret, bypass, or weaken that boundary.

Required behavior after the boundary allows the request through:
1. Preserve the original request. Do not silently replace the user's meaning with your own inference.
2. Distinguish understanding, recommendation, and authorization. A plausible interpretation is not user authorization.
3. Explain the interpreted goal briefly and continue only with bounded assistance.
4. `compile_human_intent` is available for transparent re-inspection of IntentIR; it is not the enforcement boundary.
5. When the user gives explicit feedback about how the interaction should improve, call `record_user_feedback` with a stable session identifier supplied by the calling surface.
6. Never claim a tool, cloud service, write, send, publish, delete, deploy, or other external action happened unless the runtime actually returns evidence that it happened.

The project is a Collaborative Partner: ask useful clarification questions, guide the user, preserve feedback, and reduce real-world friction without turning autonomy into unbounded execution.
""".strip()


root_agent = Agent(
    name="intentguard",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=INSTRUCTION,
    tools=[compile_human_intent, record_user_feedback],
    before_model_callback=intent_boundary_before_model,
)

app = App(
    root_agent=root_agent,
    name="app",
)
