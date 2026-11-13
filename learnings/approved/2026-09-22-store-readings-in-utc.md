---
id: 2026-09-22-store-readings-in-utc
title: Store meter readings in UTC and convert to local time only at billing export
type: decision
project: alpha
date: 2026-09-22
owner_role: TL
confidence: high
sensitivity: internal
sources: [decisions/ADR-001-store-readings-in-utc.md, https://github.com/eraserhead21/company-brain-poc/issues/2]
supersedes: none
---
**Context:** Meters report reading time in meter local time. On the daylight-saving change of 25 October 2026, local times between 02:00 and 03:00 occur twice.
**What happened:** Storing local time double-counted that hour in the test replay, with aggregates about 4% high. The team decided to convert readings to UTC at ingestion and store UTC only.
**What we learned:** Store time in UTC and convert to local time only at the billing export. Any report that shows local time must convert explicitly.
