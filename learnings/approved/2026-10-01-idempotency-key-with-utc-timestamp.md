---
id: 2026-10-01-idempotency-key-with-utc-timestamp
title: Key re-sent meter readings on meter ID and UTC timestamp, upsert on conflict
type: decision
project: alpha
date: 2026-10-01
owner_role: TL
confidence: high
sensitivity: internal
sources: [https://github.com/eraserhead21/company-brain-poc/issues/1, decisions/ADR-001-store-readings-in-utc.md]
supersedes: none
---
**Context:** Meters resend the last batch of readings after a network drop.
**What happened:** Billing totals for one meter group were 2.3% high in the sandbox on 14 Sep. Issue 1 was resolved with the key meter_id plus UTC reading_ts, upserted on conflict in the readings store. No duplicates were seen in the sandbox from 23 Sep.
**What we learned:** The idempotency key must use the same time base the store uses (UTC), so a re-sent reading gets the same key.
