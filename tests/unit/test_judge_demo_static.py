from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]


def test_firebase_hosting_targets_public_directory():
    text = (ROOT / "firebase.json").read_text(encoding="utf-8")
    assert '"public": "public"' in text
    assert '"rules": "firestore.rules"' in text


def test_judge_demo_preserves_core_intent_boundary_markers():
    text = (ROOT / "public" / "app.js").read_text(encoding="utf-8")
    assert "CLARIFY_BEFORE_EXECUTION" in text
    assert "gemini-3.7-flash" in text
    assert "GoogleAIBackend" in text
    assert "intentguard_public_feedback" in text
    assert "must not infer missing human intent or authorization" in text
    assert "intentguard.intent_plan.v1" in text
    assert "SESSION_LOCAL_ONLY" in text
    assert "external_actions: \"NONE\"" in text


def test_firestore_rules_are_default_deny_with_feedback_create_only():
    text = (ROOT / "firestore.rules").read_text(encoding="utf-8")
    assert "match /intentguard_public_feedback/{documentId}" in text
    assert "allow create: if request.auth != null" in text
    assert "allow read, update, delete: if false" in text
    assert "match /{document=**}" in text
    assert "allow read, write: if false" in text


def test_firebase_config_has_public_identifiers_but_no_server_credentials():
    text = (ROOT / "public" / "firebase-config.js").read_text(encoding="utf-8")

    # Firebase web configuration is intentionally shipped to the browser. The
    # deployment must use real identifiers, while server credentials must
    # never be placed in this public file.
    for field in ("apiKey", "projectId", "appId", "appCheckSiteKey"):
        assert re.search(rf'{field}:\s*"(?!__)[^"]+"', text), field

    for forbidden in (
        "BEGIN PRIVATE KEY",
        "private_key",
        "service_account",
        "GOOGLE_APPLICATION_CREDENTIALS",
    ):
        assert forbidden not in text
