# Project Alpha brief

Compiled: 2026-11-12T14:46:06Z, cursor 2026-11-12T14:46:06Z, by capture

## Status

- Overall: AMBER [Status 10-15]
- Firmware v2.4 rollout finished on the first 3 meter groups [Weekly 10-27]

## Key dates

- Shadow run starts 19 November 2026 [Weekly 10-27]
- Shadow run is 9 days [Weekly 10-27]
- Go-live 28 November 2026 [Status 09-30]

## Decisions

- Store all readings in UTC. Convert to local time only at the billing export [ADR-001]
- Message broker: Azure Event Hubs, Standard tier, 12 partitions keyed by meter_id [ADR-002]
- Message broker section of Solution Design v1 is replaced by Azure Event Hubs [ADR-003]
- Delivery is at-least-once, with an idempotent consumer [Design review 09-12]
- Duplicate readings: idempotency key meter_id plus UTC reading_ts, upsert on conflict [Issue 1]
- Backfill publisher throttled to 5k msg/s [PR 7]
- Shadow-run comparison window is the billing local day, 00:00 to 00:00 [Weekly 10-13]
- Mismatch gate is measured on upgraded meter groups only; v2.3 groups are held out [Status 10-01]

## Open risks

- Firmware v2.3 sends malformed timestamps; readings are rejected and logged until the customer ships the firmware fix [Risk register]
- Error logs hold raw customer data; masking is open [Risk register]
- A shadow-run mismatch above 0.1% per day blocks go-live [Risk register]

## Open conflicts

- Backfill publisher cap: "Backfill publisher throttled to 5k msg/s" [PR 7] vs "Confirmed: the backfill publisher cap is 4k msg/s" [Weekly 10-27]
- Raw readings retention: "Raw readings retained for 90 days for audit and replay" [Design v1] vs "raw readings retention is 30 days, not longer" [Weekly 09-29]
- Shadow-run sign-off owner: "Shadow-run sign-off owner: PM" [Status 10-15] vs "The Tech Lead signs off the shadow run before go-live" [Issue 12]
- Billing export interval: "Billing export interval: 15 minutes" [Weekly 10-13] vs "Billing export batch interval is 5 minutes" [Issue 12]
- On-call rota owner from October: "Engineer B owns the on-call rota from October" [Team Channel] vs "On-call rota owner from October: Engineer A" [Status 09-30]

## Scope differences

None.

## Supersessions

- Message broker: self-run Kafka cluster on AKS [Design v1], now Azure Event Hubs [ADR-003]
- Go-live: 14 November 2026 to 28 November 2026 [Status 09-30]
- Shadow run start: 17 November 2026 to 19 November 2026 [Weekly 10-13]
- Firmware v2.4 rollout: 20 October 2026 [Status 10-01], now 27 October 2026 [Weekly 10-13]
- Backfill: estimated 5 days, now about 15 days [Weekly 09-29]

## Sources

- ADR-001: Store all readings in UTC. decisions/ADR-001-store-readings-in-utc.md
- ADR-002: Message broker. decisions/ADR-002-message-broker.md
- ADR-003: Broker section of Solution Design v1. decisions/ADR-003-design-doc-broker-section.md
- Design v1: PROJECT ALPHA - SOLUTION DESIGN v1. sources/alpha-solution-design-v1.md
- Design review 09-12: PROJECT ALPHA - DESIGN REVIEW NOTES, 12 September 2026. sources/alpha-design-review-notes-2026-09-12.md
- Charter: PROJECT ALPHA - CHARTER. sources/alpha-project-charter.md
- Risk register: PROJECT ALPHA - RISK REGISTER. sources/alpha-risk-register.md
- Status 09-30: PROJECT ALPHA - STATUS UPDATE, 30 September 2026. sources/alpha-status-update-2026-09-30.md
- Status 10-01: PROJECT ALPHA - STATUS UPDATE, 1 October 2026. sources/alpha-status-update-2026-10-01.md
- Status 10-15: PROJECT ALPHA - STATUS UPDATE, 15 October 2026. sources/alpha-status-update-2026-10-15.md
- Weekly 09-29: MEETING NOTES - PROJECT ALPHA WEEKLY, 29 September 2026. sources/alpha-meeting-notes-2026-09-29-weekly.md
- Weekly 10-13: MEETING NOTES - PROJECT ALPHA WEEKLY, 13 October 2026. sources/alpha-meeting-notes-2026-10-13-weekly.md
- Weekly 10-27: MEETING NOTES - PROJECT ALPHA WEEKLY, 27 October 2026. sources/alpha-meeting-notes-2026-10-27-weekly.md
- Team Channel: TEAM CHANNEL LOG - #alpha. sources/alpha-team-channel-log-september.md
- Issue 1: ISSUE 1: Duplicate meter readings after network reconnect. https://github.com/eraserhead21/company-brain-poc/issues/1
- Issue 12: ISSUE 12: Billing export interval and shadow-run sign-off. https://github.com/eraserhead21/company-brain-poc/issues/12
- PR 7: PULL REQUEST 7: Throttle backfill publisher to 5k msg/s. https://github.com/eraserhead21/company-brain-poc/pull/7
