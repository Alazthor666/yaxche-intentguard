"""Deterministic clarification baseline used before model reasoning.

The heuristic is intentionally small and testable. It does not claim to solve
natural-language understanding; it provides auditable stop conditions for
obvious material ambiguity and authority uncertainty.

The design rule for every check below:

    stop only when two readings of the same sentence would lead the agent to
    act on a different target, a different recipient, a different scope, or a
    different reversibility.

A request that is merely vague, but where every plausible reading produces the
same safe action, is not material ambiguity. Asking there is noise, and an
assistant that asks about everything is as useless as one that assumes
everything.

```text
PLAUSIBLE_INTERPRETATION != AUTHORIZATION
VAGUE != MATERIALLY_AMBIGUOUS
STOPPING != REFUSING
```
"""

from __future__ import annotations

from dataclasses import dataclass
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
    "sort it out",
    "deal with it",
    "you know what to do",
}

# Verbs whose effect leaves the agent's own workspace and reaches a person, a
# system of record, or money. Each needs a target before it may proceed.
_OUTWARD_VERBS = r"(?:send|email|message|post|publish|share|transfer|pay|refund|charge|deploy|release)"

# Verbs whose effect cannot be undone by running the agent again.
_IRREVERSIBLE_VERBS = r"(?:delete|remove|drop|wipe|erase|purge|reset|revoke|overwrite|truncate|cancel|terminate)"

_DANGLING_PRONOUN_RE = re.compile(
    rf"^{_IRREVERSIBLE_VERBS}\s+(?:it|this|that|them|those|these|everything|all)\b"
)


@dataclass(frozen=True)
class _Stop:
    unknowns: list[str]
    question: str


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _has_explicit_recipient(lower: str) -> bool:
    if "@" in lower:
        return True
    if re.search(rf"\b{_OUTWARD_VERBS}\b[^.!?]{{0,160}}\bto\s+\S+", lower):
        return True
    if re.search(r"\brecipient\s+(?:is|=)\s+\S+", lower):
        return True
    if re.search(r"\bwith\s+(?:the\s+)?(?:team|client|customer|group)\b", lower):
        return True
    return False


def _has_authorization_uncertainty(lower: str) -> bool:
    patterns = (
        r"\b(?:whether|if)\b[^.!?]{0,100}\bauthori[sz]",
        r"\bdo not assume\b[^.!?]{0,120}\bauthori[sz]",
        r"\bdon't assume\b[^.!?]{0,120}\bauthori[sz]",
        r"\bwithout assuming\b[^.!?]{0,120}\bauthori[sz]",
        r"\bnot sure\b[^.!?]{0,80}\b(?:allowed|permitted|approved)",
    )
    return any(re.search(pattern, lower) for pattern in patterns)


def _has_concrete_target(lower: str) -> bool:
    """A quoted name, a path, an id, or an explicit noun after the verb."""
    if re.search(r"[\"'`][^\"'`]{2,}[\"'`]", lower):
        return True
    if re.search(r"[/\\][\w.-]+", lower):
        return True
    if re.search(r"\b(?:named|called|id|uuid|ticket|issue|pr)\s+\S+", lower):
        return True
    return False


def _has_unnegated(lower: str, verb_group: str) -> bool:
    """True when the verb appears as a request, not as a prohibition.

    "Do not send it" contains `send`, but the user is forbidding the action, not
    asking for it. Treating that as an outward request produces exactly the kind
    of pointless question that makes a clarifying agent unusable.
    """
    for match in re.finditer(rf"\b{verb_group}\b", lower):
        window = lower[max(0, match.start() - 40):match.start()]
        if re.search(r"\b(?:do not|don't|never|without|avoid|refrain from|no)\b[\w\s,]{0,25}$", window):
            continue
        return True
    return False


def _detect_outward_stop(lower: str) -> _Stop | None:
    """Actions that reach outside the agent need a known recipient."""
    if not _has_unnegated(lower, _OUTWARD_VERBS):
        return None

    unknowns: list[str] = []
    if not _has_explicit_recipient(lower):
        unknowns.append("recipient")
    if _has_authorization_uncertainty(lower):
        unknowns.append("execution authorization")

    if not unknowns:
        return None

    # Name the action the user actually used. "Are you authorizing me to send
    # it" reads naturally for an email and absurdly for a refund.
    verb = "send" if re.search(r"\b(?:send|email|message)\b", lower) else "do"

    if unknowns == ["recipient"]:
        question = "Who should receive it?"
    elif unknowns == ["execution authorization"]:
        question = f"Are you authorizing me to {verb} it, or only to help prepare it?"
    else:
        question = (
            f"Who should receive it, and are you authorizing me to {verb} it "
            "or only to help prepare it?"
        )
    return _Stop(unknowns, question)


def _detect_irreversible_stop(lower: str) -> _Stop | None:
    """Irreversible verbs need an unambiguous target before proceeding."""
    if not re.match(rf"^{_IRREVERSIBLE_VERBS}\b", lower):
        return None
    if not _has_unnegated(lower, _IRREVERSIBLE_VERBS):
        return None
    if _DANGLING_PRONOUN_RE.match(lower):
        return _Stop(
            ["exact target of an irreversible action"],
            "This cannot be undone. Which exact item should I act on?",
        )
    if not _has_concrete_target(lower):
        return _Stop(
            ["exact target of an irreversible action"],
            "This cannot be undone. Which exact item should I act on?",
        )
    return None


def _detect_money_stop(lower: str) -> _Stop | None:
    """Money moves need an amount and a destination, never an inferred one."""
    if not re.search(r"\b(?:pay|transfer|refund|charge|invoice|wire|reimburse)\b", lower):
        return None
    has_amount = re.search(r"(?:[$€£¥]\s?\d|\b\d+(?:[.,]\d+)?\s*(?:usd|eur|mxn|dollars|pesos)\b)", lower)
    has_destination = _has_explicit_recipient(lower)
    unknowns = []
    if not has_amount:
        unknowns.append("amount")
    if not has_destination:
        unknowns.append("payee")
    if not unknowns:
        return None
    return _Stop(
        unknowns,
        "Money movement needs both an exact amount and an exact payee. "
        f"Missing: {', '.join(unknowns)}.",
    )


def _detect_scope_stop(lower: str) -> _Stop | None:
    """A quantifier over an unbounded set changes blast radius."""
    if not re.search(r"\b(?:all|every|everything|entire|whole)\b", lower):
        return None
    if not re.search(rf"\b{_IRREVERSIBLE_VERBS}\b|\b{_OUTWARD_VERBS}\b", lower):
        return None
    if _has_concrete_target(lower):
        return None
    return _Stop(
        ["scope of the affected set"],
        "This would affect an unbounded set. Which exact items are in scope?",
    )


def _detect_access_stop(lower: str) -> _Stop | None:
    """Sharing without naming the level is materially ambiguous.

    "Share the doc with the team" names a recipient but not what they may do
    with it. View and edit are different blast radii, so the recipient alone is
    not enough to proceed.
    """
    grants_access = re.search(
        r"\b(?:share|grant|give)\b[^.!?]{0,60}\b(?:access|permission|rights)\b", lower
    )
    shares_with = re.search(r"\bshare\b[^.!?]{0,80}\bwith\s+\S+", lower)
    if not (grants_access or shares_with):
        return None
    if not _has_unnegated(lower, r"(?:share|grant|give)"):
        return None
    if re.search(
        r"\b(?:read[- ]only|view(?:er)?|edit(?:or)?|write|admin|owner|comment)\b", lower
    ):
        return None
    return _Stop(
        ["access level"],
        "What level of access should they get — view, comment, edit, or admin?",
    )


# Order matters: the most consequential class wins so the question the user
# sees is about the thing that could hurt most.
_DETECTORS = (
    _detect_money_stop,
    _detect_irreversible_stop,
    _detect_scope_stop,
    _detect_access_stop,
    _detect_outward_stop,
)


def _constraints_for(lower: str) -> list[str]:
    constraints: list[str] = []
    if " without " in lower:
        constraints.append("contains an explicit 'without' restriction")
    if " before " in lower:
        constraints.append("contains an explicit deadline/order constraint")
    if " must " in lower:
        constraints.append("contains an explicit mandatory condition")
    if "do not assume" in lower or "don't assume" in lower:
        constraints.append("must not infer missing human intent or authorization")
    if re.search(r"\bdo not (?:send|publish|share|delete)\b", lower):
        constraints.append("explicitly forbids an outward or irreversible action")
    return constraints


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

    # Brevity is not ambiguity. "Delete /etc/hosts" is two words and perfectly
    # specific; "handle it" is two words and says nothing. What separates them
    # is whether a concrete target is named, not how many words were used.
    too_short = len(lower.split()) < 3 and not _has_concrete_target(lower)
    if lower in _GENERIC_REQUESTS or too_short:
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

    constraints = _constraints_for(lower)

    for detector in _DETECTORS:
        stop = detector(lower)
        if stop is not None:
            return IntentIR(
                original_request=text,
                normalized_goal=text,
                constraints=constraints,
                unknowns=stop.unknowns,
                material_ambiguity=True,
                clarification_question=stop.question,
                status="CLARIFY_BEFORE_EXECUTION",
            )

    return IntentIR(
        original_request=text,
        normalized_goal=text,
        constraints=constraints,
        material_ambiguity=False,
        status="CLEAR_ENOUGH",
    )
