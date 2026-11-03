---
id: 2026-10-01-idempotency-key-for-resent-readings
title: Deduplicate resent meter readings with an idempotency key and upsert
type: learning
project: alpha
date: 2026-10-01
owner_role: Engineer
confidence: high
sensitivity: internal
sources: [https://github.com/eraserhead21/claude-org-poc/issues/1]
supersedes: none
---
**Context:** Meters resend the last batch of readings after a network drop.
**What happened:** In the sandbox on 14 September, billing totals for one meter group were 2.3% high. The fix uses the key meter_id plus UTC reading_ts, with upsert on conflict. No duplicates were seen after 23 September.
**What we learned:** Deduplicate on a natural key with an upsert. Test by dropping the head-end link for 60 seconds and restoring it.
