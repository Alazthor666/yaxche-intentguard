import pytest
from pydantic import ValidationError

from app.contracts import IntentIR


def test_clear_intent_contract_accepts_clear_state():
    item = IntentIR(
        original_request="Summarize this report into five bullets",
        normalized_goal="Summarize this report into five bullets",
    )
    assert item.status == "CLEAR_ENOUGH"
    assert item.material_ambiguity is False


def test_material_ambiguity_requires_question():
    with pytest.raises(ValidationError):
        IntentIR(
            original_request="Do it",
            normalized_goal="Do it",
            material_ambiguity=True,
            status="CLARIFY_BEFORE_EXECUTION",
        )


def test_material_ambiguity_requires_stop_status():
    with pytest.raises(ValidationError):
        IntentIR(
            original_request="Do it",
            normalized_goal="Do it",
            material_ambiguity=True,
            clarification_question="What specifically should I do?",
            status="CLEAR_ENOUGH",
        )
