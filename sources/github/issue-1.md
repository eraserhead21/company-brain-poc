<!-- Snapshot of GitHub issue #1 in eraserhead21/company-brain-poc, taken 2026-11-12 by scripts/snapshot_github.py.
Fictional test data: every name, contact detail, secret and commercial term
below is planted for the redaction test. Capture reads GitHub;
the brief and cards cite the URL, and the checks read this file. -->

ISSUE 1: Duplicate meter readings after network reconnect

Created: 2026-10-01. State: closed.

Meters resend the last batch of readings after a network drop. Billing totals for meter group G7 were 2.3% high in the sandbox on 14 Sep. Repro: drop the head-end link for 60 s and restore.

Comment, 2026-10-01:

Resolution: idempotency key meter_id + UTC reading_ts, upsert on conflict in the readings store. No duplicates in the sandbox since 23 Sep.
