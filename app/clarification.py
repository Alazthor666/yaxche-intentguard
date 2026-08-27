"""Deterministic clarification baseline used before model reasoning.

The heuristic is intentionally small and testable. It does not claim to solve
natural-language understanding; it provides auditable stop conditions for
obvious material ambiguity and authority uncertainty.
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


def _has_send_action(lower: str) -> bool:
    return re.search(r"\b(send|sending|sent|email|emailing|emailed)\b", lower) is not None


def _has_explicit_recipient(lower: str) -> bool:
    if "@" in lower:
        return True
    if re.search(r"\bsend\b[^.!?]{0,160}\bto\s+\S+", lower):
        return True
    if re.search(r"\brecipient\s+(?:is|=)\s+\S+", lower):
        return True
    return False


def _has_authorization_uncertainty(lower: str) -> bool:
    auth = r"authori[sz]\w*"
    patterns = (
        # Direct uncertainty around authorization, including inflections such as
        # authorize/authorized/authorizing/authorization.
        rf"\b(?:whether|if)\b[^.!?]{{0,120}}\b{auth}\b",
        rf"\b(?:may|might|maybe|possibly|unclear|unsure|uncertain)\b[^.!?]{{0,140}}\b{auth}\b",
        # Explicit denial or withholding of execution authority.
        rf"\b(?:not|never)\s+{auth}\b",
        rf"\bdo\s+not\s+{auth}\b",
        # Permission synonyms and future/conditional approval.
        r"\bif\b[^.!?]{0,120}\b(?:allowed|permitted|approved)\b",
        rf"\b(?:only\s+)?after\b[^.!?]{{0,120}}\b(?:approve\w*|confirm\w*|{auth})\b",
        # Existing explicit 'do not assume' forms.
        rf"\bdo not assume\b[^.!?]{{0,120}}\b{auth}\b",
        rf"\bdon't assume\b[^.!?]{{0,120}}\b{auth}\b",
        rf"\bwithout assuming\b[^.!?]{{0,120}}\b{auth}\b",
    )
    return any(re.search(pattern, lower) for pattern in patterns)


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

    constraints: list[str] = []
    if " without " in lower:
        constraints.append("contains an explicit 'without' restriction")
    if " before " in lower or " after " in lower:
        constraints.append("contains an explicit deadline/order constraint")
    if " must " in lower:
        constraints.append("contains an explicit mandatory condition")
    if "do not assume" in lower or "don't assume" in lower:
        constraints.append("must not infer missing human intent or authorization")

    if _has_send_action(lower):
        unknowns: list[str] = []
        if not _has_explicit_recipient(lower):
            unknowns.append("recipient")
        if _has_authorization_uncertainty(lower):
            unknowns.append("execution authorization")

        if unknowns:
            if unknowns == ["recipient"]:
                question = "Who should receive it?"
            elif unknowns == ["execution authorization"]:
                question = "Are you authorizing me to send it, or only to help prepare it?"
            else:
                question = (
                    "Who should receive it, and are you authorizing me to send it "
                    "or only to help prepare it?"
                )

            return IntentIR(
                original_request=text,
                normalized_goal=text,
                constraints=constraints,
                unknowns=unknowns,
                material_ambiguity=True,
                clarification_question=question,
                status="CLARIFY_BEFORE_EXECUTION",
            )

    if lower.startswith("delete ") and not any(
        marker in lower for marker in (" named ", " id ", " path ", "/", "\\")
    ):
        return IntentIR(
            original_request=text,
            normalized_goal=text,
            constraints=constraints,
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
            constraints=constraints,
            unknowns=["publication destination"],
            material_ambiguity=True,
            clarification_question="Where should this be published?",
            status="CLARIFY_BEFORE_EXECUTION",
        )

    return IntentIR(
        original_request=text,
        normalized_goal=text,
        constraints=constraints,
        material_ambiguity=False,
        status="CLEAR_ENOUGH",
    )
