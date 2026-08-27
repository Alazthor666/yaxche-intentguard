# Firestore Live Gate — 2026-08-27

Status: PASS (human-observed Cloud Shell execution)

Project: `gen-lang-client-0554159756` (`YAXCHE IntentGuard Hackathon`)
Database: `(default)`
Adapter exercised: `app.storage.FirestoreFeedbackStore`
Collection: `intentguard_feedback`

## Evidence boundary

This receipt records terminal output supplied directly by the human operator from Google Cloud Shell. It is not an independently fetched Cloud Audit Log. No secret values are included.

Observed output:

```text
=== YAXCHE INTENTGUARD FIRESTORE LIVE GATE ===
WRITE_OK
{'session_id': 'intentguard-firestore-live-gate-20260827', 'feedback': 'Live Firestore persistence gate for the All Things Agentic Hackathon.', 'recorded_at': '2026-08-27T14:19:32.057271+00:00', 'store': 'firestore'}
READ_COUNT=1
READ_OK
1MOiGWThd2TYKLT5irmd
{'feedback': 'Live Firestore persistence gate for the All Things Agentic Hackathon.', 'recorded_at': '2026-08-27T14:19:32.057271+00:00', 'store': 'firestore', 'session_id': 'intentguard-firestore-live-gate-20260827'}
DELETE_OK
FIRESTORE_LIVE_GATE=PASS
```

## Claims supported

```text
FIRESTORE_DATABASE_CREATED = true
FIRESTORE_LIVE_WRITE_PROVEN = true
FIRESTORE_LIVE_READ_PROVEN = true
FIRESTORE_LIVE_DELETE_PROVEN = true
FIRESTORE_LIVE_USE_PROVEN = true
CLOUD_RUN_DEPLOYMENT_PROVEN = false
HOSTED_URL_AVAILABLE = false
VERIFIED = false
```

The test document was deleted after read-back, so the live gate does not intentionally leave test data behind.
