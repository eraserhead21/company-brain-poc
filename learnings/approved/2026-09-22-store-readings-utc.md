---
id: 2026-09-22-store-readings-utc
title: Store all meter readings in UTC to handle daylight-saving transitions
type: decision
project: alpha
date: 2026-09-22
owner_role: TL
confidence: high
sensitivity: internal
sources: [decisions/ADR-001-store-readings-in-utc.md, https://github.com/eraserhead21/claude-org-poc/issues/2]
supersedes: none
---

**Context:** Meters report readings with timestamps in local time. On daylight-saving transitions, local times between 02:00 and 03:00 occur twice.

**What happened:** A test replay of DST-overlapping readings showed aggregates about 4% high. Storing local timestamps causes double-counting.

**What we learned:** Convert all meter readings to UTC at ingestion time and store only UTC. Convert to local time only in the billing export. This prevents double-counting, makes the idempotency key work correctly, and simplifies cross-timezone reporting.
