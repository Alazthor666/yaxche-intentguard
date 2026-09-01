from app.clarification import compile_intent, decompose_intent


LIVE_AUTH_CONTEXT = (
    "I need to send an important report today. Help me do it, but do not assume "
    "who should receive it or whether I have authorized sending it."
)


def test_subordinate_comma_stays_inside_one_intent_atom():
    atoms = decompose_intent(LIVE_AUTH_CONTEXT)
    assert atoms == [LIVE_AUTH_CONTEXT]

    result = compile_intent(LIVE_AUTH_CONTEXT)
    assert result.material_ambiguity is True
    assert result.unknowns == ["recipient", "execution authorization"]


def test_strong_coordination_markers_create_independent_atoms():
    assert decompose_intent("Summarize the notes and write a haiku") == [
        "Summarize the notes",
        "write a haiku",
    ]
    assert decompose_intent("Draft the title; summarize the notes") == [
        "Draft the title",
        "summarize the notes",
    ]
