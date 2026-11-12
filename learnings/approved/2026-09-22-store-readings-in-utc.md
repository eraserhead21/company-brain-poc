---
id: 2026-09-22-store-readings-in-utc
title: Store all meter readings in UTC and convert only at the billing export
type: decision
project: alpha
date: 2026-09-22
owner_role: TL
confidence: high
sensitivity: internal
sources: [decisions/ADR-001-store-readings-in-utc.md, https://github.com/eraserhead21/company-brain-poc/issues/2]
supersedes: none
---
**Context:** Meters report reading times in local time. On the daylight-saving change, local times between 02:00 and 03:00 occur twice.
**What happened:** Storing local time double-counted that hour. Aggregates for that day were about 4% high in the test replay. ADR-001 switched storage to UTC.
**What we learned:** Store one time base and convert only at the edge (the billing export). Any report that shows local time must convert explicitly.
