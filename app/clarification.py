"""Deterministic clarification baseline used before model reasoning.

The heuristic is intentionally small and testable. It does not claim to solve
natural-language understanding; it provides an auditable stop condition for
obvious material ambiguity.
"""

from __future__ import annotations

import re

from .contracts import IntentIR


_GENERIC_REQUESTS = {
    "do it",
    "fix it",
    "handle it",
    "handle this",
    "make it better",
    "take care of it",
    "take care of this",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def compile_intent(request: str) -> IntentIR:
    """Compile an obvious first-pass IntentIR from raw human text."""

    text = _normalize(request)
    if not text:
        return IntentIR(
            original_request="(empty request)",
            normalized_goal="Clarify the user's intended outcome",
            unknowns=["goal"],
            material_ambiguity=True,
            clarification_question="What would you like me to accomplish?",
            status="CLARIFY_BEFORE_EXECUTION",
        )

    lower = text.casefold().rstrip(".!?")

    if lower in _GENERIC_REQUESTS or len(lower.split()) < 3:
        return IntentIR(
            original_request=text,
            normalized_goal=text,
            unknowns=["specific outcome", "target"],
            material_ambiguity=True,
            clarification_question=(
                "What specific outcome should I produce, and what should I act on?"
            ),
            status="CLARIFY_BEFORE_EXECUTION",
        )

    if lower.startswith("send ") and not any(
        marker in lower for marker in (" to ", " email ", "@")
    ):
        return IntentIR(
            original_request=text,
            normalized_goal=text,
            unknowns=["recipient"],
            material_ambiguity=True,
            clarification_question="Who should receive it?",
            status="CLARIFY_BEFORE_EXECUTION",
        )

    if lower.startswith("delete ") and not any(
        marker in lower for marker in (" named ", " id ", " path ", "/", "\\")
    ):
        return IntentIR(
            original_request=text,
            normalized_goal=text,
            unknowns=["exact deletion target"],
            material_ambiguity=True,
            clarification_question="Which exact item should be deleted?",
            status="CLARIFY_BEFORE_EXECUTION",
        )

    if lower.startswith("publish ") and not any(
        marker in lower for marker in (" on ", " to ", " at ")
    ):
        return IntentIR(
            original_request=text,
            normalized_goal=text,
            unknowns=["publication destination"],
            material_ambiguity=True,
            clarification_question="Where should this be published?",
            status="CLARIFY_BEFORE_EXECUTION",
        )

    constraints: list[str] = []
    if " without " in lower:
        constraints.append("contains an explicit 'without' restriction")
    if " before " in lower:
        constraints.append("contains an explicit deadline/order constraint")
    if " must " in lower:
        constraints.append("contains an explicit mandatory condition")

    return IntentIR(
        original_request=text,
        normalized_goal=text,
        constraints=constraints,
        material_ambiguity=False,
        status="CLEAR_ENOUGH",
    )
