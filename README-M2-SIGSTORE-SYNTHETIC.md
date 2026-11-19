# OCTO M2 E4 — GitHub / Sigstore synthetic-origin demonstration

**Synthetic-only development candidate. Never production.**
This public GitHub Free test repo contains no Agrilatin data, customer records,
Neon credentials, n8n credentials, actual send requests, or vendor events.

A branch-triggered GitHub Actions job generates a deliberately synthetic event with
an unpredictable nonce and GitHub SHA/run/attempt identity, validates its shape
and 120-second generation freshness, and requests an in-toto SLSA provenance
attestation through GitHub OIDC and Sigstore using actions/attest.

GitHub's signing ceremony establishes provenance of the *test artifact* from this
GitHub Actions job. It does NOT prove that a real external business event occurred.
The workflow, repository and artifact producer remain under the owner's control.
It is **not** the required Cloudflare D1 independent witness, not an independently
custodied vendor signing key, not a Neon origin record, and not a Stage I acceptance.

The branch must remain unmerged and unconnected to production. The action has
no outbound email, campaign, workflow activation, Cloudflare or Neon credentials.
Its granted permissions are only contents:read, id-token:write and
attestations:write for producing the GitHub-owned attestation.

Upon success, use the workflow artifact and:
  gh attestation verify octo-m2-synthetic-source.json -R Utsavsharan/ocho-m2-synthetic-producer

This verification checks the signed provenance using GitHub's attestation
service and Sigstore trust, not merely a locally generated checksum.
Check the verified workflow SHA, repository and branch as a separate decision.

**Acceptance status:** E4 TRUE_UPSTREAM_ORIGIN = NO-GO, M2 = NO-GO,
Stage I FINAL_PASS = NO-GO; this workflow is solely a positive live
infrastructure test of the attestation mechanism.
