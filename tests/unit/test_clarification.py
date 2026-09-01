from app.clarification import analyze_intent_atoms, compile_intent, decompose_intent


def test_generic_request_stops_for_clarification():
    result = compile_intent("Do it")
    assert result.material_ambiguity is True
    assert result.status == "CLARIFY_BEFORE_EXECUTION"
    assert result.clarification_question


def test_send_without_recipient_stops():
    result = compile_intent("Send the report")
    assert result.material_ambiguity is True
    assert "recipient" in result.unknowns
    assert result.clarification_question == "Who should receive it?"


def test_embedded_send_without_recipient_stops():
    result = compile_intent("I need to send an important report today")
    assert result.material_ambiguity is True
    assert "recipient" in result.unknowns
    assert result.status == "CLARIFY_BEFORE_EXECUTION"


def test_live_gate_prompt_detects_recipient_and_authorization_uncertainty():
    result = compile_intent(
        "I need to send an important report today. Help me do it, but do not assume "
        "who should receive it or whether I have authorized sending it."
    )
    assert result.material_ambiguity is True
    assert result.status == "CLARIFY_BEFORE_EXECUTION"
    assert "recipient" in result.unknowns
    assert "execution authorization" in result.unknowns
    assert result.clarification_question == (
        "Who should receive it, and are you authorizing me to send it "
        "or only to help prepare it?"
    )
    assert "must not infer missing human intent or authorization" in result.constraints


def test_send_with_explicit_recipient_can_continue():
    result = compile_intent("Send the report to alice@example.com")
    assert result.material_ambiguity is False
    assert result.status == "CLEAR_ENOUGH"


def test_specific_request_can_continue():
    result = compile_intent("Summarize this report into five bullet points")
    assert result.material_ambiguity is False
    assert result.status == "CLEAR_ENOUGH"


def test_delete_without_exact_target_stops():
    result = compile_intent("Delete the file")
    assert result.material_ambiguity is True
    assert result.status == "CLARIFY_BEFORE_EXECUTION"


# ── negation: a prohibition is not a request ─────────────────────────────────
# Without this, "do not send anything" reads as a send request and the agent
# asks who the recipient is. An assistant that asks about everything is as
# useless as one that assumes everything.

def test_forbidden_outward_action_is_not_treated_as_a_request():
    result = compile_intent(
        "Draft a concise executive summary of this project for a hackathon judge. "
        "Do not send or publish anything."
    )
    assert result.material_ambiguity is False
    assert result.status == "CLEAR_ENOUGH"
    assert "explicitly forbids an outward or irreversible action" in result.constraints


def test_forbidden_deletion_is_not_treated_as_a_request():
    result = compile_intent("Do not delete anything, just list the files")
    assert result.material_ambiguity is False


# ── money: amount and payee are both required ────────────────────────────────

def test_payment_without_amount_or_payee_stops():
    result = compile_intent("Pay the invoice")
    assert result.material_ambiguity is True
    assert "amount" in result.unknowns
    assert "payee" in result.unknowns


def test_transfer_with_amount_and_payee_can_continue():
    result = compile_intent("Transfer 500 USD to alice@example.com")
    assert result.material_ambiguity is False


def test_payment_missing_only_amount_names_only_that_gap():
    result = compile_intent("Refund the customer at billing@example.com")
    assert result.material_ambiguity is True
    assert result.unknowns == ["amount"]


# ── irreversible: a dangling pronoun is not a target ─────────────────────────

def test_irreversible_verb_with_dangling_pronoun_stops():
    result = compile_intent("Wipe them from the system")
    assert result.material_ambiguity is True
    assert "This cannot be undone" in result.clarification_question


def test_polite_irreversible_request_without_target_stops():
    result = compile_intent("Please delete it")
    assert result.material_ambiguity is True
    assert result.unknowns == ["exact target of an irreversible action"]

def test_irreversible_verb_with_named_target_can_continue():
    result = compile_intent("Delete the file named archive.zip")
    assert result.material_ambiguity is False


def test_irreversible_verb_with_path_can_continue():
    result = compile_intent("Remove build/artifacts/stale.log")
    assert result.material_ambiguity is False


# ── scope: an unbounded quantifier changes blast radius ──────────────────────

def test_unbounded_scope_on_destructive_action_stops():
    result = compile_intent("Delete all the old records")
    assert result.material_ambiguity is True


def test_unbounded_scope_without_destructive_action_can_continue():
    result = compile_intent("Summarize all the meeting notes into three bullets")
    assert result.material_ambiguity is False


# ── access: a recipient without a level is still ambiguous ───────────────────

def test_share_without_access_level_stops():
    result = compile_intent("Share the roadmap doc with the team")
    assert result.material_ambiguity is True
    assert result.unknowns == ["access level"]


def test_share_with_explicit_access_level_can_continue():
    result = compile_intent("Share the roadmap doc with the team as read-only")
    assert result.material_ambiguity is False


def test_grant_access_without_level_stops():
    result = compile_intent("Grant access to the repo")
    assert result.material_ambiguity is True


# ── the most consequential class wins the question ───────────────────────────

def test_money_outranks_recipient_when_both_are_unknown():
    result = compile_intent("Pay whoever sent the invoice")
    assert result.material_ambiguity is True
    assert "amount" in result.unknowns


# ── harmless work must never be interrupted ──────────────────────────────────

def test_ordinary_creative_request_is_not_interrupted():
    for request in (
        "Write a haiku about the sea",
        "Refactor this function without changing its public API",
        "Explain how the intent boundary works",
    ):
        result = compile_intent(request)
        assert result.material_ambiguity is False, request


# ── atomic intent vaccines ────────────────────────────────────────────────────

def test_atomic_decomposition_prevents_target_leakage_between_clauses():
    result = compile_intent("Draft a note for ticket 123 and delete it")
    assert result.material_ambiguity is True
    assert result.unknowns == ["exact target of an irreversible action"]
    assert "blocking atom 2/2: irreversible" in result.constraints


def test_atomic_decomposition_prevents_recipient_leakage_between_clauses():
    result = compile_intent("Email a summary to alice@example.com and publish the post")
    assert result.material_ambiguity is True
    assert result.unknowns == ["recipient"]
    assert "blocking atom 2/2: outward" in result.constraints


def test_spanish_trojan_clause_is_caught_atomically():
    request = "Redacta un correo amable para el cliente y borra los logs de la base de datos"
    atoms = decompose_intent(request)
    result = compile_intent(request)

    assert atoms == [
        "Redacta un correo amable para el cliente",
        "borra los logs de la base de datos",
    ]
    assert result.material_ambiguity is True
    assert "blocking atom 2/2: irreversible" in result.constraints
    assert (
        "sensitive target detected; downstream policy/authorization must fail closed"
        in result.constraints
    )


def test_presumption_cannot_supply_current_high_impact_parameters():
    result = compile_intent("Transfer 500 USD to the usual account")
    assert result.material_ambiguity is True
    assert result.unknowns == ["current explicit target/recipient/parameters"]
    assert "blocking atom 1/1: presumption" in result.constraints


def test_pressure_is_recorded_but_does_not_create_false_ambiguity():
    result = compile_intent("Urgent: summarize the meeting notes into three bullets")
    assert result.material_ambiguity is False
    assert "urgency/pressure detected; pressure does not expand authority" in result.constraints


def test_pressure_never_repairs_an_existing_ambiguity():
    result = compile_intent("Urgent: send the report now")
    assert result.material_ambiguity is True
    assert result.unknowns == ["recipient"]
    assert "urgency/pressure detected; pressure does not expand authority" in result.constraints


def test_risk_signal_is_not_mislabeled_as_ambiguity_when_target_is_exact():
    result = compile_intent("Delete the file named archive.zip immediately")
    assert result.material_ambiguity is False
    assert (
        "high-impact action detected; downstream explicit authorization remains required"
        in result.constraints
    )
    assert "urgency/pressure detected; pressure does not expand authority" in result.constraints


def test_historical_style_preference_does_not_overblock_safe_work():
    result = compile_intent("Write the summary in the usual tone")
    assert result.material_ambiguity is False
    assert (
        "historical/default-context language detected; current authorization cannot be inferred"
        in result.constraints
    )


def test_atom_analysis_exposes_signals_without_granting_authority():
    analyses = analyze_intent_atoms(
        "Draft a customer note and urgently delete the database logs"
    )
    assert len(analyses) == 2
    assert analyses[0]["material_stop"] is False
    assert analyses[1]["pressure_detected"] is True
    assert analyses[1]["high_impact_action_detected"] is True
    assert analyses[1]["sensitive_action_detected"] is True
    assert analyses[1]["material_stop"] is True
    assert analyses[1]["boundary_rule"] == "irreversible"


def test_two_benign_atoms_do_not_create_a_false_stop():
    result = compile_intent("Summarize the notes and write a haiku")
    assert result.material_ambiguity is False
