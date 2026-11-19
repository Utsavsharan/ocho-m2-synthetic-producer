#!/usr/bin/env python3
"""Produce a PUBLIC, SYNTHETIC-ONLY M2 test artifact. Never read customer inputs."""
import hashlib
import json
import os
from pathlib import Path
import secrets
from datetime import datetime, timezone

EXPECTED_REPO = "Utsavsharan/ocho-m2-synthetic-producer"
PAYLOAD = "OCTO_TEST_ONLY_NO_CUSTOMER_DATA_NO_REAL_OUTREACH"
SCHEMA = "octo-m2-github-synthetic-source-v1"

def main():
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise SystemExit("REFUSE: must run under GitHub Actions (synthetic-only)")
    if os.environ.get("GITHUB_REPOSITORY", "").lower() != EXPECTED_REPO.lower():
        raise SystemExit("REFUSE: unexpected source repository")
    sha = os.environ.get("GITHUB_SHA", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "")
    if len(sha) != 40 or not all(c in "0123456789abcdef" for c in sha):
        raise SystemExit("REFUSE: missing valid commit SHA")
    if not run_id.isdigit() or not attempt.isdigit():
        raise SystemExit("REFUSE: missing run identity")
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    doc = {
        "schema": SCHEMA,
        "test_only": True,
        "real_customer_origin": False,
        "m2_live_acceptance": False,
        "kind": "SYNTHETIC_PROVENANCE_DEMONSTRATION_NOT_VENDOR_SOURCE",
        "event_id": "OCTO-SYNTHETIC-GHA-" + secrets.token_hex(16),
        "observed_utc": stamp,
        "payload_sha256": hashlib.sha256(PAYLOAD.encode("ascii")).hexdigest(),
        "payload_is_fixed_synthetic_constant": True,
        "source": {
            "repository": EXPECTED_REPO,
            "commit_sha": sha,
            "run_id": run_id,
            "run_attempt": int(attempt),
            "ref": os.environ.get("GITHUB_REF", "")
        },
        "limits": [
            "NO_REAL_NEON_OR_N8N_EVENT",
            "NOT_EXTERNAL_CLOUDFLARE_D1_WITNESS",
            "NOT_INDEPENDENT_VENDOR_ORIGIN",
            "NOT_STAGE_I_FINAL_PASS"
        ]
    }
    out = Path("artifacts/octo-m2-synthetic-source.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8") as fh:
        json.dump(doc, fh, sort_keys=True, separators=(",", ":"))
        fh.write("\n")
    print("SYNTHETIC_ARTIFACT_CREATED", out, "SHA256",
          hashlib.sha256(out.read_bytes()).hexdigest())

if __name__ == "__main__":
    main()
