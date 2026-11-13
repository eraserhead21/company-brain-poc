---
id: 2026-10-01-idempotency-key-for-meter-resends
title: Key each reading on meter_id and UTC timestamp so a resend overwrites the reading
type: learning
project: alpha
date: 2026-10-01
owner_role: Engineer
confidence: high
sensitivity: internal
sources: [https://github.com/eraserhead21/company-brain-poc/issues/1, sources/alpha-meeting-notes-2026-09-29-weekly.md]
supersedes: none
---
**Context:** Meters resend the last batch of readings after a network drop.
**What happened:** In the sandbox on 14 Sep, billing totals for meter group G7 were 2.3% high. The fix uses the idempotency key meter_id plus UTC reading_ts, with upsert on conflict in the readings store. No duplicates were seen in the sandbox from 23 Sep.
**What we learned:** Make the readings write idempotent on meter and UTC timestamp, so a resend overwrites the reading instead of adding to the total.
