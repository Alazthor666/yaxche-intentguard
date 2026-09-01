"""Deterministic clarification baseline used before model reasoning.

IntentGuard does not try to solve language understanding. It enforces auditable
pre-model stop conditions when materially different readings could change the
target, recipient, scope, reversibility, money movement, access, or authorization.

The V1.1 "atomic vaccines" add a second invariant: independent goals inside one
message must not lend each other missing context. A benign first clause cannot
launder a dangerous or ambiguous second clause.

```text
PLAUSIBLE_INTERPRETATION != AUTHORIZATION
VAGUE != MATERIALLY_AMBIGUOUS
STOPPING != REFUSING
PRESSURE != AUTHORITY
HISTORICAL_DEFAULT != CURRENT_AUTHORIZATION
ONE_CLEAR_ATOM != WHOLE_REQUEST_CLEAR
RISK_SIGNAL != MATERIAL_AMBIGUITY
MENTIONED_OBJECT != REQUESTED_ACTION
```
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from .contracts import IntentIR


_GENERIC_REQUESTS = {
    "do it", "fix it", "handle it", "handle this", "make it better",
    "take care of it", "take care of this", "sort it out", "deal with it",
    "you know what to do", "hazlo", "arreglalo", "arréglalo", "encargate",
    "encárgate", "hazte cargo", "ya sabes", "tu sabes que hacer", "tú sabes qué hacer",
}

_OUTWARD_VERBS = r"(?:send|email|message|post|publish|share|transfer|pay|refund|charge|deploy|release|envia|envía|enviar|manda|mandar|publica|publicar|comparte|compartir|transfiere|transferir|paga|pagar|reembolsa|reembolsar|cobra|cobrar|despliega|desplegar)"
_IRREVERSIBLE_VERBS = r"(?:delete|remove|drop|wipe|erase|purge|reset|revoke|overwrite|truncate|cancel|terminate|borra|borrar|elimina|eliminar|suprime|suprimir|vacía|vacia|vaciar|revoca|revocar|sobrescribe|sobrescribir|trunca|truncar|cancela|cancelar|termina|terminar)"
# Only action verbs belong here. Objects such as "invoice/factura" must not be
# treated as money movement merely because they are mentioned in a safe request.
_MONEY_VERBS = r"(?:pay|transfer|refund|charge|wire|reimburse|paga|pagar|transfiere|transferir|reembolsa|reembolsar|cobra|cobrar|facturar)"
_ACCESS_VERBS = r"(?:share|grant|give|comparte|compartir|otorga|otorgar|da|dar)"

_PRESUMPTION_PATTERNS = (
    r"\bas usual\b", r"\bthe usual\b", r"\bsame as always\b", r"\byou know(?: the one)?\b",
    r"\bdefault (?:account|address|recipient|destination|settings?)\b", r"\bcomo siempre\b",
    r"\blo habitual\b", r"\bya sabes\b", r"\bcomo ya sabes\b", r"\bde costumbre\b",
    r"\b(?:la |el )?(?:direcci[oó]n|cuenta|destino|configuraci[oó]n) de siempre\b",
)
_PRESSURE_PATTERNS = (
    r"\burgent(?:ly)?\b", r"\bright now\b", r"\bno time\b", r"\bdo it now\b",
    r"\bimmediately\b", r"\basap\b", r"\burgente\b", r"\bahora mismo\b",
    r"\bno hay tiempo\b", r"\bhazlo ya\b", r"\binmediatamente\b", r"\bperderemos? (?:la )?cuenta\b",
)
_SENSITIVE_TARGET_PATTERNS = (
    r"\blogs?\b", r"\bdatabase\b", r"\bbase de datos\b", r"\bpasswords?\b",
    r"\bcontrase(?:ñ|n)as?\b", r"\bcredentials?\b", r"\bcredenciales\b",
    r"\bconfiguration\b", r"\bconfiguraci[oó]n\b", r"\bpermissions?\b", r"\bpermisos?\b",
    r"\bproduction\b", r"\bproducci[oó]n\b", r"\baccess\b", r"\bacceso\b",
)

_DANGLING_PRONOUN_RE = re.compile(rf"^{_IRREVERSIBLE_VERBS}\s+(?:it|this|that|them|those|these|everything|all|eso|esto|aquello|ellos|ellas|todo|todos|todas)\b")

# Independent goals are separated only by strong coordination markers. A comma
# can introduce subordinate authorization context and therefore stays inside the
# same atom.
_ATOM_SPLIT_RE = re.compile(
    r"\s*(?:;|\b(?:and|then|also|plus|y|adem[aá]s|tambi[eé]n|luego|por cierto)\b)\s*",
    flags=re.IGNORECASE,
)

@dataclass(frozen=True)
class _Stop:
    unknowns: list[str]
    question: str
    rule: str


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def decompose_intent(request: str) -> list[str]:
    text = _normalize(request)
    if not text:
        return []
    return [atom for atom in (_normalize(part) for part in _ATOM_SPLIT_RE.split(text)) if atom]


def _matches_any(lower: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, lower, flags=re.IGNORECASE) for pattern in patterns)


def _has_presumption(lower: str) -> bool:
    return _matches_any(lower, _PRESUMPTION_PATTERNS)


def _has_pressure(lower: str) -> bool:
    return _matches_any(lower, _PRESSURE_PATTERNS)


def _has_sensitive_target(lower: str) -> bool:
    return _matches_any(lower, _SENSITIVE_TARGET_PATTERNS)


def _has_explicit_recipient(lower: str) -> bool:
    if "@" in lower:
        return True
    if re.search(rf"\b{_OUTWARD_VERBS}\b[^.!?]{{0,160}}\b(?:to|a|para)\s+\S+", lower):
        return True
    if re.search(r"\b(?:recipient|destinatario|destinataria)\s+(?:is|es|=)\s+\S+", lower):
        return True
    return bool(re.search(r"\b(?:with|con)\s+(?:the\s+|el\s+|la\s+)?(?:team|client|customer|group|equipo|cliente|grupo)\b", lower))


def _has_authorization_uncertainty(lower: str) -> bool:
    patterns = (
        r"\b(?:whether|if)\b[^.!?]{0,100}\bauthori[sz]", r"\bdo not assume\b[^.!?]{0,120}\bauthori[sz]",
        r"\bdon't assume\b[^.!?]{0,120}\bauthori[sz]", r"\bwithout assuming\b[^.!?]{0,120}\bauthori[sz]",
        r"\bnot sure\b[^.!?]{0,80}\b(?:allowed|permitted|approved)", r"\b(?:si|no s[eé] si)\b[^.!?]{0,100}\bautoriza",
        r"\bno (?:asumas?|supongas?)\b[^.!?]{0,120}\bautoriza", r"\bsin (?:asumir|suponer)\b[^.!?]{0,120}\bautoriza",
    )
    return any(re.search(pattern, lower) for pattern in patterns)


def _has_concrete_target(lower: str) -> bool:
    return bool(
        re.search(r"[\"'`][^\"'`]{2,}[\"'`]", lower)
        or re.search(r"(?:^|\s)(?:[a-zA-Z]:)?[/\\][\w.\-/\\]+", lower)
        or re.search(r"\b[\w.-]+(?:[/\\][\w.-]+)+\b", lower)
        or re.search(r"\b(?:named|called|id|uuid|ticket|issue|pr|llamado|llamada|folio|archivo|file|rama|branch)\s+\S+", lower)
    )


def _has_unnegated(lower: str, verb_group: str) -> bool:
    for match in re.finditer(rf"\b{verb_group}\b", lower):
        window = lower[max(0, match.start() - 48):match.start()]
        if re.search(r"\b(?:do not|don't|never|without|avoid|refrain from|no|nunca|sin|evita|evitar)\b[\w\s,áéíóúñü]{0,30}$", window):
            continue
        return True
    return False


def _has_high_impact_action(lower: str) -> bool:
    return any(_has_unnegated(lower, group) for group in (_OUTWARD_VERBS, _IRREVERSIBLE_VERBS, _MONEY_VERBS, _ACCESS_VERBS))


def _detect_presumption_stop(lower: str) -> _Stop | None:
    if _has_presumption(lower) and _has_high_impact_action(lower):
        return _Stop(["current explicit target/recipient/parameters"], "This request relies on a historical/default assumption. What exact current target, recipient, scope, and parameters should I use?", "presumption")
    return None


def _detect_outward_stop(lower: str) -> _Stop | None:
    if not _has_unnegated(lower, _OUTWARD_VERBS):
        return None
    unknowns: list[str] = []
    if not _has_explicit_recipient(lower):
        unknowns.append("recipient")
    if _has_authorization_uncertainty(lower):
        unknowns.append("execution authorization")
    if not unknowns:
        return None
    verb = "send" if re.search(r"\b(?:send|email|message|envia|envía|enviar|manda|mandar)\b", lower) else "do"
    if unknowns == ["recipient"]:
        question = "Who should receive it?"
    elif unknowns == ["execution authorization"]:
        question = f"Are you authorizing me to {verb} it, or only to help prepare it?"
    else:
        question = f"Who should receive it, and are you authorizing me to {verb} it or only to help prepare it?"
    return _Stop(unknowns, question, "outward")


def _detect_irreversible_stop(lower: str) -> _Stop | None:
    if not _has_unnegated(lower, _IRREVERSIBLE_VERBS):
        return None
    if _DANGLING_PRONOUN_RE.match(lower) or not _has_concrete_target(lower):
        return _Stop(["exact target of an irreversible action"], "This cannot be undone. Which exact item should I act on?", "irreversible")
    return None


def _detect_money_stop(lower: str) -> _Stop | None:
    if not _has_unnegated(lower, _MONEY_VERBS):
        return None
    has_amount = re.search(r"(?:[$€£¥]\s?\d|\b\d+(?:[.,]\d+)?\s*(?:usd|eur|mxn|dollars?|pesos?|d[oó]lares?)\b)", lower)
    unknowns: list[str] = []
    if not has_amount:
        unknowns.append("amount")
    if not _has_explicit_recipient(lower):
        unknowns.append("payee")
    if not unknowns:
        return None
    return _Stop(unknowns, "Money movement needs both an exact amount and an exact payee. " f"Missing: {', '.join(unknowns)}.", "money")


def _detect_scope_stop(lower: str) -> _Stop | None:
    if not re.search(r"\b(?:all|every|everything|entire|whole|todos?|todas?|todo|cada|completo|completa)\b", lower):
        return None
    if not (_has_unnegated(lower, _IRREVERSIBLE_VERBS) or _has_unnegated(lower, _OUTWARD_VERBS)):
        return None
    if _has_concrete_target(lower):
        return None
    return _Stop(["scope of the affected set"], "This would affect an unbounded set. Which exact items are in scope?", "scope")


def _detect_access_stop(lower: str) -> _Stop | None:
    grants_access = re.search(rf"\b{_ACCESS_VERBS}\b[^.!?]{{0,60}}\b(?:access|permission|rights|acceso|permiso|permisos)\b", lower)
    shares_with = re.search(r"\b(?:share|comparte|compartir)\b[^.!?]{0,80}\b(?:with|con)\s+\S+", lower)
    if not (grants_access or shares_with) or not _has_unnegated(lower, _ACCESS_VERBS):
        return None
    if re.search(r"\b(?:read[- ]only|view(?:er)?|edit(?:or)?|write|admin|owner|comment|solo lectura|lectura|ver|comentar|editar|escritura|administrador|administradora|propietario|propietaria)\b", lower):
        return None
    return _Stop(["access level"], "What level of access should they get — view, comment, edit, or admin?", "access")


_DETECTORS = (_detect_presumption_stop, _detect_money_stop, _detect_irreversible_stop, _detect_scope_stop, _detect_access_stop, _detect_outward_stop)


def _constraints_for(lower: str) -> list[str]:
    constraints: list[str] = []
    if " without " in lower or " sin " in lower:
        constraints.append("contains an explicit 'without/sin' restriction")
    if " before " in lower or " antes " in lower:
        constraints.append("contains an explicit deadline/order constraint")
    if " must " in lower or " debe " in lower:
        constraints.append("contains an explicit mandatory condition")
    if "do not assume" in lower or "don't assume" in lower or "no asumas" in lower or "no supongas" in lower:
        constraints.append("must not infer missing human intent or authorization")
    if re.search(rf"\b(?:do not|no)\s+(?:{_OUTWARD_VERBS}|{_IRREVERSIBLE_VERBS})\b", lower):
        constraints.append("explicitly forbids an outward or irreversible action")
    return constraints


def _atomic_signal_constraints(atoms_lower: list[str]) -> list[str]:
    constraints: list[str] = []
    if len(atoms_lower) > 1:
        constraints.append(f"atomic intent decomposition applied: {len(atoms_lower)} clauses")
    if any(_has_pressure(atom) for atom in atoms_lower):
        constraints.append("urgency/pressure detected; pressure does not expand authority")
    if any(_has_high_impact_action(atom) for atom in atoms_lower):
        constraints.append("high-impact action detected; downstream explicit authorization remains required")
    if any(_has_sensitive_target(atom) and _has_high_impact_action(atom) for atom in atoms_lower):
        constraints.append("sensitive target detected; downstream policy/authorization must fail closed")
    if any(_has_presumption(atom) for atom in atoms_lower):
        constraints.append("historical/default-context language detected; current authorization cannot be inferred")
    return constraints


def analyze_intent_atoms(request: str) -> list[dict[str, object]]:
    analyses: list[dict[str, object]] = []
    for index, atom in enumerate(decompose_intent(request)):
        lower = atom.casefold().rstrip(".!?")
        stop = next((candidate for detector in _DETECTORS if (candidate := detector(lower)) is not None), None)
        analyses.append({
            "index": index, "atom": atom, "pressure_detected": _has_pressure(lower),
            "presumption_detected": _has_presumption(lower), "high_impact_action_detected": _has_high_impact_action(lower),
            "sensitive_action_detected": _has_sensitive_target(lower) and _has_high_impact_action(lower),
            "material_stop": stop is not None, "boundary_rule": stop.rule if stop else None,
            "unknowns": list(stop.unknowns) if stop else [],
        })
    return analyses


def compile_intent(request: str) -> IntentIR:
    text = _normalize(request)
    if not text:
        return IntentIR(original_request="(empty request)", normalized_goal="Clarify the user's intended outcome", unknowns=["goal"], material_ambiguity=True, clarification_question="What would you like me to accomplish?", status="CLARIFY_BEFORE_EXECUTION")

    lower = text.casefold().rstrip(".!?")
    too_short = len(lower.split()) < 3 and not _has_concrete_target(lower)
    if lower in _GENERIC_REQUESTS or too_short:
        return IntentIR(original_request=text, normalized_goal=text, unknowns=["specific outcome", "target"], material_ambiguity=True, clarification_question="What specific outcome should I produce, and what should I act on?", status="CLARIFY_BEFORE_EXECUTION")

    atoms_lower = [atom.casefold().rstrip(".!?") for atom in decompose_intent(text)]
    constraints = list(dict.fromkeys(_constraints_for(lower) + _atomic_signal_constraints(atoms_lower)))

    for index, atom_lower in enumerate(atoms_lower):
        if atom_lower in _GENERIC_REQUESTS:
            return IntentIR(original_request=text, normalized_goal=text, constraints=constraints + [f"blocking atom {index + 1}/{len(atoms_lower)}: generic intent"], unknowns=["specific outcome", "target"], material_ambiguity=True, clarification_question="What specific outcome should I produce, and what should I act on?", status="CLARIFY_BEFORE_EXECUTION")

    for detector in _DETECTORS:
        for index, atom_lower in enumerate(atoms_lower):
            stop = detector(atom_lower)
            if stop is not None:
                return IntentIR(original_request=text, normalized_goal=text, constraints=constraints + [f"blocking atom {index + 1}/{len(atoms_lower)}: {stop.rule}"], unknowns=stop.unknowns, material_ambiguity=True, clarification_question=stop.question, status="CLARIFY_BEFORE_EXECUTION")

    return IntentIR(original_request=text, normalized_goal=text, constraints=constraints, material_ambiguity=False, status="CLEAR_ENOUGH")
