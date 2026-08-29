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


def test_firebase_config_contains_no_server_secret_material():
    """Guard the thing that would actually be a breach.

    An earlier version of this test asserted the placeholders were still in
    place. That was the right worry enforced the wrong way: it made the demo
    permanently undeployable, since going live means filling them in.

    Firebase web configuration is public by design — the API key identifies the
    project and authorizes nothing, and the reCAPTCHA site key is bound
    server-side to the allowed domain. The real boundary is firestore.rules,
    covered above. What must never appear here is server-side credential
    material.

        WEB_CLIENT_IDENTIFIER != SERVER_SECRET
    """
    text = (ROOT / "public" / "firebase-config.js").read_text(encoding="utf-8")

    forbidden = (
        "-----BEGIN",           # any PEM private key block
        "private_key",          # service account JSON field
        "client_secret",        # OAuth client secret
        "refresh_token",
        "service_account",
        "AIzaSyA_SERVER",       # placeholder shape for a server-restricted key
    )
    for marker in forbidden:
        assert marker not in text, f"server secret material in client config: {marker}"

    # A partially wired config is worse than an unwired one: it half-initializes
    # and fails in ways that look like a bug rather than a missing setup step.
    concrete = [
        line for line in ("apiKey", "appId", "projectId")
        if f'{line}: "__' not in text
    ]
    assert len(concrete) in (0, 3), (
        f"firebase-config.js is partially wired: {concrete} concrete, the rest placeholders"
    )
