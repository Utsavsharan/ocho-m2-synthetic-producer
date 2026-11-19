#!/usr/bin/env python3
"""Fail-closed shape and freshness check for the synthetic-only manifest."""
import hashlib
import json
import os
from pathlib import Path
import re
from datetime import datetime, timezone

EXPECTED_REPO = "Utsavsharan/ocho-m2-synthetic-producer"
PAYLOAD = "OCTO_TEST_ONLY_NO_CUSTOMER_DATA_NO_REAL_OUTREACH"

def verify(path):
    raw = Path(path).read_bytes()
    if len(raw) > 8192:
        raise ValueError("oversized artifact")
    doc = json.loads(raw)
    if type(doc) is not dict or doc.get("schema") != "octo-m2-github-synthetic-source-v1":
        raise ValueError("wrong schema")
    if doc.get("test_only") is not True or doc.get("real_customer_origin") is not False:
        raise ValueError("could be mislabeled as real event")
    if doc.get("m2_live_acceptance") is not False:
        raise ValueError("could be mislabeled as live acceptance")
    if doc.get("kind") != "SYNTHETIC_PROVENANCE_DEMONSTRATION_NOT_VENDOR_SOURCE":
        raise ValueError("unknown source kind")
    if not re.fullmatch(r"OCTO-SYNTHETIC-GHA-[0-9a-f]{32}", str(doc.get("event_id", ""))):
        raise ValueError("invalid nonce")
    if doc.get("payload_is_fixed_synthetic_constant") is not True:
        raise ValueError("payload must be synthetic constant")
    if doc.get("payload_sha256") != hashlib.sha256(PAYLOAD.encode("ascii")).hexdigest():
        raise ValueError("payload hash mismatch")
    src = doc.get("source")
    if type(src) is not dict or src.get("repository", "").lower() != EXPECTED_REPO.lower():
        raise ValueError("unexpected producer")
    if not re.fullmatch(r"[0-9a-f]{40}", str(src.get("commit_sha", ""))):
        raise ValueError("missing producer commit")
    if not str(src.get("run_id", "")).isdigit() or type(src.get("run_attempt")) is not int:
        raise ValueError("missing producer run identity")
    if not isinstance(src.get("ref"), str):
        raise ValueError("missing producer ref")
    if os.getenv("GITHUB_ACTIONS") == "true":
        if src["commit_sha"] != os.getenv("GITHUB_SHA"):
            raise ValueError("commit not bound to workflow")
        if src["run_id"] != os.getenv("GITHUB_RUN_ID"):
            raise ValueError("run not bound to workflow")
        if src["run_attempt"] != int(os.getenv("GITHUB_RUN_ATTEMPT", "0")):
            raise ValueError("attempt not bound to workflow")
    try:
        observed = datetime.fromisoformat(doc["observed_utc"].replace("Z", "+00:00"))
    except (KeyError, ValueError, AttributeError) as exc:
        raise ValueError("bad observed time") from exc
    if observed.tzinfo is None:
        raise ValueError("naive timestamp")
    age = (datetime.now(timezone.utc) - observed).total_seconds()
    if age < -15 or age > 120:
        raise ValueError("not fresh for signing test")
    required_limits = {
        "NO_REAL_NEON_OR_N8N_EVENT",
        "NOT_EXTERNAL_CLOUDFLARE_D1_WITNESS",
        "NOT_INDEPENDENT_VENDOR_ORIGIN",
        "NOT_STAGE_I_FINAL_PASS"
    }
    if type(doc.get("limits")) is not list or set(doc["limits"]) != required_limits:
        raise ValueError("missing refusal labels")
    return hashlib.sha256(raw).hexdigest()

if __name__ == "__main__":
    try:
        digest = verify("artifacts/octo-m2-synthetic-source.json")
        print("SYNTHETIC_SHAPE_AND_FRESHNESS_PASS", digest)
    except Exception as exc:
        raise SystemExit("REFUSED: " + str(exc))
