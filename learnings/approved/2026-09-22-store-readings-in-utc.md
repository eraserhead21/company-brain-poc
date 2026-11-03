---
id: 2026-09-22-store-readings-in-utc
title: Store all readings in UTC, convert to local time only at billing export
type: decision
project: alpha
date: 2026-09-22
owner_role: TL
confidence: high
sensitivity: internal
sources: [decisions/ADR-001-store-readings-in-utc.md, sources/alpha-team-channel-log-september.md]
supersedes: none
---
**Context:** Meters report reading time in local time. The DST change on 25 Oct 2026 repeats local hours.
**What happened:** ADR-001 was accepted. The team agreed in the channel on 21 Sep to store UTC. Storing local time double counts the repeated hour.
**What we learned:** Store time in UTC. Convert to local time only where a report needs it.
