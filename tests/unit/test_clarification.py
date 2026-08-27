from app.clarification import compile_intent


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
