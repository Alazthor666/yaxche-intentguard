"""Google ADK root agent for YAXCHÉ IntentGuard."""

from __future__ import annotations

import os

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from .clarification import compile_intent
from .storage import record_feedback


MODEL = os.getenv("INTENTGUARD_MODEL", "gemini-3.5-flash")


def compile_human_intent(request: str) -> dict:
    """Compile raw human text into a structured IntentIR before action."""

    return compile_intent(request).model_dump()


def record_user_feedback(session_id: str, feedback: str) -> dict[str, str]:
    """Persist explicit user feedback through the configured storage adapter."""

    return record_feedback(session_id=session_id, feedback=feedback)


INSTRUCTION = """
You are YAXCHÉ IntentGuard, a collaborative agent that protects human intent before action.

Required behavior:
1. For every new actionable request, call `compile_human_intent` before proposing execution.
2. Preserve the original request. Do not silently replace the user's meaning with your own inference.
3. If the returned IntentIR has `material_ambiguity=true`, ask exactly the smallest useful clarification question and STOP the action path until the user answers.
4. If the IntentIR is CLEAR_ENOUGH, explain the interpreted goal briefly and continue with bounded assistance.
5. Distinguish understanding, recommendation, and authorization. A plausible interpretation is not user authorization.
6. When the user gives explicit feedback about how the interaction should improve, call `record_user_feedback` with a stable session identifier supplied by the calling surface.
7. Never claim a tool, cloud service, write, send, publish, delete, deploy, or other external action happened unless the runtime actually returns evidence that it happened.

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
)

app = App(
    root_agent=root_agent,
    name="app",
)
