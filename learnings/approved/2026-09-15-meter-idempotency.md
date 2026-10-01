---
id: 2026-09-15-meter-idempotency
title: Meter duplicates after network drops; use meter ID plus timestamp for idempotency
type: decision
project: alpha
date: 2026-09-15
owner_role: Engineer
confidence: high
sensitivity: internal
sources: [https://github.com/eraserhead21/claude-org-poc/issues/1, https://github.com/eraserhead21/claude-org-poc/pull/7]
supersedes: none
---

**Context:** Meters resend the last batch of readings after a network drop, causing duplicate totals. A test showed meter group totals 2.3% high after a simulated 60-second link loss.

**What happened:** Implemented an idempotency key of meter ID plus UTC reading timestamp, using upsert-on-conflict in the readings store. No duplicates have been observed since implementation on 23 September.

**What we learned:** Deduplicate resent meter readings using the combination of meter identifier and UTC timestamp as the idempotency key. This handles network-drop scenarios without requiring per-reading sequence numbers.
