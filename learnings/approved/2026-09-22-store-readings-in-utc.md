---
id: 2026-09-22-store-readings-in-utc
title: Store meter readings in UTC and convert only at billing export
type: decision
project: alpha
date: 2026-09-22
owner_role: TL
confidence: high
sensitivity: internal
sources: [decisions/ADR-001-store-readings-in-utc.md, sources/alpha-team-channel-log-september.md]
supersedes: none
---
**Context:** Meter local time repeats one hour at the daylight-saving change on 25 October 2026.
**What happened:** Storing local time double-counts that hour. The team agreed on 21 September to store UTC. ADR-001 was accepted on 22 September.
**What we learned:** Convert reading_ts to UTC at ingestion. Convert to local time only in the billing export. Any local-time report must convert explicitly.
