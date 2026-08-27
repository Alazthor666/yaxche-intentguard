from app.agent import build_intent_guard_response


LIVE_GATE_PROMPT = (
    "I need to send an important report today. Help me do it, but do not assume "
    "who should receive it or whether I have authorized sending it."
)


def test_pre_model_boundary_blocks_material_ambiguity():
    response = build_intent_guard_response(LIVE_GATE_PROMPT)
    assert response is not None
    assert response.content is not None
    assert response.content.parts
    text = response.content.parts[0].text
    assert text is not None
    assert "INTENTGUARD_GATE=CLARIFY_BEFORE_EXECUTION" in text
    assert '"material_ambiguity": true' in text
    assert '"status": "CLARIFY_BEFORE_EXECUTION"' in text
    assert '"recipient"' in text
    assert '"execution authorization"' in text


def test_pre_model_boundary_allows_clear_request_to_reach_model():
    response = build_intent_guard_response(
        "Summarize this report into five bullet points"
    )
    assert response is None
