# Project Alpha brief

Compiled: 2026-11-03T16:06:32Z, cursor 2026-11-03T16:06:32Z, by capture

## Status

- Amber, as of 15 Oct. Go-live 28 Nov. [Status 10-15]
- Backfill re-planned to about 15 days. Test re-run at 5k msg/s is pending. [Status 10-01]
- Firmware v2.3 meters are held out of the shadow run until they upgrade. [Status 10-01]

## Key dates

- Design sign-off 19 Sep. [Status 09-22]
- Firmware v2.4 rollout 27 Oct. [Weekly 10-13; Status 10-15]
- DST change 25 Oct: local times 02:00 to 03:00 occur twice. [ADR-001]
- Shadow run starts 19 Nov. [Weekly 10-13; Status 10-15]
- Go-live 28 Nov. [Status 10-15]

## Decisions

- Store readings in UTC. Convert to local time only in the billing export. [ADR-001]
- Broker: Azure Event Hubs Standard, 12 partitions keyed by meter_id. [ADR-002]
- Deduplicate resent readings with key meter_id plus UTC reading_ts, upsert on conflict. [Issue 1]
- Throttle the backfill publisher to 5k msg/s. [PR 7; Issue 3]
- Retain raw readings 30 days. [Weekly 09-29]
- Shadow gate is measured on upgraded meter groups only. [Status 10-01]

## Open risks

- Firmware v2.3 sends malformed timestamps, for example 2026-13-01. Readings are rejected and logged. Owner TL. [Issue 5; Risks R1]
- Error logs hold raw request bodies with customer data. Masking is open. Owner Engineer. [Issue 6; Risks R3]
- Shadow mismatch above 0.1% would block go-live. Daily dashboard review from day 1. Owner PM. Dashboard is open. [Risks R4; Issue 4]
- Backfill takes about 15 days at the throttle. Owner TL. [Risks R2]

## Open conflicts

- Broker. Kafka on AKS, 3 brokers, 12 partitions. [Design v1] Versus Azure Event Hubs Standard, 12 partitions. [ADR-002] Neither source says it replaces the other. Acting on the wrong one changes the design.
- On-call rota owner from October. Engineer A. [Channel Sep 09-29] Versus Engineer B. [Status 09-30] Acting on the wrong one changes the owner.
- Billing export interval. 5 minutes. [Issue 12] Versus 15 minutes. [Weekly 10-13] Neither replaces the other. Acting on the wrong one changes the design.
- Shadow-run sign-off owner. Tech Lead. [Issue 12] Versus PM. [Status 10-15] Acting on the wrong one changes the owner.

## Supersessions

- Shadow run 3 Nov, then 17 Nov, moved to 19 Nov. [Charter; Status 09-30] to [Weekly 10-13; Status 10-15]
- Firmware v2.4 fix 20 Oct moved to 27 Oct. [Status 10-01] to [Weekly 10-13; Status 10-15]
- Backfill complete 17 Oct. No longer holds; no new date. [Charter] [Weekly 09-29]
- Raw readings retention 90 days moved to 30 days. [Design v1] to [Weekly 09-29]
- Readings stored in meter local time moved to UTC. [Design v1] to [Status 09-30; ADR-001]
- Shadow gate covers all meter groups moved to upgraded groups only. [Charter] to [Status 10-01]

## Sources

- Charter: Alpha - Project Charter. sources/alpha-project-charter.md
- Design v1: Alpha - Solution Design v1. sources/alpha-solution-design-v1.md
- Kickoff: Alpha - Meeting Notes 2026-09-15 Kickoff. sources/alpha-meeting-notes-2026-09-15-kickoff.md
- Weekly 09-29: Alpha - Meeting Notes 2026-09-29 Weekly. sources/alpha-meeting-notes-2026-09-29-weekly.md
- Weekly 10-13: Alpha - Meeting Notes 2026-10-13 Weekly. sources/alpha-meeting-notes-2026-10-13-weekly.md
- Status 09-22: Alpha - Status Update 2026-09-22. sources/alpha-status-update-2026-09-22.md
- Status 09-30: Alpha - Status Update 2026-09-30. sources/alpha-status-update-2026-09-30.md
- Status 10-01: Alpha - Status Update 2026-10-01. sources/alpha-status-update-2026-10-01.md
- Status 10-15: Alpha - Status Update 2026-10-15. sources/alpha-status-update-2026-10-15.md
- Risks: Alpha - Risk Register. sources/alpha-risk-register.md
- Channel Sep: Alpha - Team Channel Log (September). sources/alpha-team-channel-log-september.md
- ADR-001: decisions/ADR-001-store-readings-in-utc.md
- ADR-002: decisions/ADR-002-message-broker.md
- Issue 1: https://github.com/eraserhead21/claude-org-poc/issues/1
- Issue 3: https://github.com/eraserhead21/claude-org-poc/issues/3
- Issue 4: https://github.com/eraserhead21/claude-org-poc/issues/4
- Issue 5: https://github.com/eraserhead21/claude-org-poc/issues/5
- Issue 6: https://github.com/eraserhead21/claude-org-poc/issues/6
- Issue 12: https://github.com/eraserhead21/claude-org-poc/issues/12
- PR 7: https://github.com/eraserhead21/claude-org-poc/pull/7
