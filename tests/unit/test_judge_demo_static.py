from pathlib import Path


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


def test_firestore_rules_are_default_deny_with_feedback_create_only():
    text = (ROOT / "firestore.rules").read_text(encoding="utf-8")
    assert "match /intentguard_public_feedback/{documentId}" in text
    assert "allow create: if request.auth != null" in text
    assert "allow read, update, delete: if false" in text
    assert "match /{document=**}" in text
    assert "allow read, write: if false" in text


def test_firebase_config_contains_no_real_secret_material_yet():
    text = (ROOT / "public" / "firebase-config.js").read_text(encoding="utf-8")
    assert "__FIREBASE_WEB_API_KEY__" in text
    assert "__FIREBASE_WEB_APP_ID__" in text
    assert "__RECAPTCHA_ENTERPRISE_SITE_KEY__" in text
