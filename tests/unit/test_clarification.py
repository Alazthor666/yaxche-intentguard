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


def test_specific_request_can_continue():
    result = compile_intent("Summarize this report into five bullet points")
    assert result.material_ambiguity is False
    assert result.status == "CLEAR_ENOUGH"


def test_delete_without_exact_target_stops():
    result = compile_intent("Delete the file")
    assert result.material_ambiguity is True
    assert result.status == "CLARIFY_BEFORE_EXECUTION"
