# Project Alpha brief

Compiled: 2026-11-12T14:38:00Z, cursor 2026-11-12T14:38:00Z, by capture

## Status
- Overall AMBER at the last status update, 15 October. [Status 10-15]
- Go-live is 28 November 2026. [Status 09-30]
- Shadow-run gate: under 0.1% daily mismatch for 7 days. [Charter]

## Key dates
- Firmware v2.4 rollout: 27 October. [Meeting 10-13]
- Shadow run starts: 19 November. [Meeting 10-13]
- Go-live: 28 November. [Status 09-30]

## Decisions
- Readings are stored in UTC and converted only at the billing export. [ADR-001]
- Message broker: Azure Event Hubs, Standard tier, 12 partitions keyed by meter_id. [ADR-002]
- Re-sent readings are matched by meter_id and UTC reading_ts, with upsert on conflict. [Issue 1]
- Backfill publisher is throttled to 5k msg/s. The 18-month backfill is planned at about 15 days. [PR 7] [Meeting 09-29]

## Open risks
- Firmware v2.3 meters send malformed timestamps. Northwind owns the fix. [Issue 5]
- Meters on v2.3 are held out of the shadow run until they upgrade. [Status 10-01]
- Error logs hold customer details. Masking is still open. [Issue 6] [Risk register]
- A shadow-run mismatch above 0.1% would block go-live. [Risk register]

## Open conflicts
- Billing export batch interval: "Billing export interval: 15 minutes" [Meeting 10-13] versus "Billing export batch interval is 5 minutes" [Issue 12].
- Shadow-run sign-off owner: "Shadow-run sign-off owner: PM" [Status 10-15] versus "The Tech Lead signs off the shadow run before go-live" [Issue 12].
- On-call rota owner from October: "Engineer B owns the on-call rota from October" [Channel Sep] versus "On-call rota owner from October: Engineer A" [Status 09-30].
- Raw readings retention: "Raw readings retained for 90 days for audit and replay" [Design v1] versus "Agreed: raw readings retention is 30 days, not longer" [Meeting 09-29].
- Message broker: "Kafka on AKS, 3 brokers, 12 partitions keyed by meter_id" [Design v1] versus "Use Azure Event Hubs (Standard tier, 12 partitions, keyed by meter_id)" [ADR-002].

## Scope differences
None.

## Supersessions
- Go-live: 14 November 2026 is replaced by 28 November 2026. [Charter] [Status 09-30]
- Shadow run start: 17 November is replaced by 19 November. [Status 09-30] [Meeting 10-13]
- Firmware v2.4 rollout: 20 October is replaced by 27 October. [Status 10-01] [Meeting 10-13]

## Sources
- Charter: PROJECT ALPHA - CHARTER, version 1.0. sources/alpha-project-charter.md
- Design v1: PROJECT ALPHA - SOLUTION DESIGN v1. sources/alpha-solution-design-v1.md
- Status 09-30: PROJECT ALPHA - STATUS UPDATE, 30 September 2026. sources/alpha-status-update-2026-09-30.md
- Status 10-01: PROJECT ALPHA - STATUS UPDATE, 1 October 2026. sources/alpha-status-update-2026-10-01.md
- Status 10-15: PROJECT ALPHA - STATUS UPDATE, 15 October 2026. sources/alpha-status-update-2026-10-15.md
- Meeting 09-29: MEETING NOTES - PROJECT ALPHA WEEKLY, 29 September 2026. sources/alpha-meeting-notes-2026-09-29-weekly.md
- Meeting 10-13: MEETING NOTES - PROJECT ALPHA WEEKLY, 13 October 2026. sources/alpha-meeting-notes-2026-10-13-weekly.md
- Channel Sep: TEAM CHANNEL LOG - #alpha, September. sources/alpha-team-channel-log-september.md
- Risk register: PROJECT ALPHA - RISK REGISTER, last updated 30 September 2026. sources/alpha-risk-register.md
- ADR-001: Store all readings in UTC. decisions/ADR-001-store-readings-in-utc.md
- ADR-002: Message broker. decisions/ADR-002-message-broker.md
- Issue 1: Duplicate meter readings after network reconnect. https://github.com/eraserhead21/company-brain-poc/issues/1
- Issue 5: Firmware v2.3 sends malformed timestamps. https://github.com/eraserhead21/company-brain-poc/issues/5
- Issue 6: Customer data in error logs. https://github.com/eraserhead21/company-brain-poc/issues/6
- Issue 12: Billing export interval and shadow-run sign-off. https://github.com/eraserhead21/company-brain-poc/issues/12
- PR 7: Throttle backfill publisher to 5k msg/s. https://github.com/eraserhead21/company-brain-poc/pull/7
