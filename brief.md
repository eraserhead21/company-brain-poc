# Project Alpha brief

Compiled: 2026-11-03T15:25:44Z, cursor 2026-11-03T15:25:44Z, by capture

## Status
- Overall AMBER. Go-live 28 Nov 2026. [Status 10-01]
- Design signed off 19 Sep 2026. [Status 09-22]
- Duplicate-reading fix in place: idempotency key on meter ID and UTC reading time. [Issue 1]
- Backfill of 18 months needs about 15 days at a 5,000 msg/s cap. [Weekly 09-29] [PR 7] [Issue 3]
- Next: re-run the one-month backfill test at 5,000 msg/s. [Status 10-01]

## Key dates
- 19 Sep 2026: design sign-off. [Status 09-22]
- 20 Oct 2026: customer firmware v2.4 fix ships. [Status 10-01]
- 25 Oct 2026: DST change, local-time readings repeat. [ADR-001]
- 17 Nov 2026: shadow run starts. [Status 09-30]
- 28 Nov 2026: go-live. [Status 10-01]

## Decisions
- Store all readings in UTC. Convert to local time only in the billing export. [ADR-001]
- Broker: Azure Event Hubs, Standard tier, 12 partitions keyed by meter ID. [ADR-002]
- Idempotency key: meter ID plus UTC reading time. Upsert on conflict. [Issue 1] [handler.py]
- Raw readings retained 30 days. [Weekly 09-29]
- Shadow-run gate (under 0.1% daily mismatch for 7 days) measured on upgraded meter groups only. [Charter] [Status 10-01]
- Backfill publisher capped at 5,000 msg/s. [PR 7] [backfill.py]

## Open risks
- Firmware v2.3 sends malformed timestamps. Malformed readings are rejected and logged. Owner TL. [Risk Register] [Issue 5]
- Backfill takes about 15 days at the cap. Owner TL. [Risk Register]
- Customer details in error logs. Masking before logging is open. Owner Engineer. [Risk Register] [Issue 6]
- Shadow-run mismatch above 0.1% would block go-live. Owner PM. [Risk Register]
- Exactly-once versus at-least-once delivery is an open question. The idempotency key is in place, but no source records a decision. [Design v1] [Issue 1]

## Open conflicts
- Broker: Kafka on AKS, 3 brokers, 12 partitions [Design v1] versus Azure Event Hubs, 12 partitions [ADR-002]. ADR-002 does not say it replaces the design doc.
- Backfill complete: 17 Oct 2026 [Charter] versus about 15 days with no new date [Weekly 09-29] [Status 09-30].
- On-call owner from October: one Engineer [Channel Log] versus a different Engineer [Status 09-30].
- Duplicate-reading fix merged: "last week" [Weekly 09-29] versus "this week" [Status 09-30].

## Supersessions
- Go-live 14 Nov 2026 [Charter] to 28 Nov 2026 [Status 09-30]. Reason: firmware and backfill duration.
- Shadow run start 3 Nov 2026 [Charter] to 17 Nov 2026 [Status 09-30].
- Shadow gate on all meter groups [Charter] to upgraded groups only [Status 10-01].
- Backfill 5 days [Design v1] to about 15 days [Weekly 09-29].
- Raw retention 90 days [Design v1] to 30 days [Weekly 09-29].
- DST handling open question [Design v1] to store UTC [ADR-001] [Status 09-30].
- Firmware fix with no date [Issue 5] to ships 20 Oct 2026 [Status 10-01].

## Sources
- Charter: Alpha - Project Charter, sources/alpha-project-charter.md
- Design v1: Alpha - Solution Design v1, sources/alpha-solution-design-v1.md
- Kickoff 09-15: Alpha - Meeting Notes 2026-09-15 Kickoff, sources/alpha-meeting-notes-2026-09-15-kickoff.md
- Weekly 09-29: Alpha - Meeting Notes 2026-09-29 Weekly, sources/alpha-meeting-notes-2026-09-29-weekly.md
- Status 09-22: Alpha - Status Update 2026-09-22, sources/alpha-status-update-2026-09-22.md
- Status 09-30: Alpha - Status Update 2026-09-30, sources/alpha-status-update-2026-09-30.md
- Status 10-01: Alpha - Status Update 2026-10-01, sources/alpha-status-update-2026-10-01.md
- Risk Register: Alpha - Risk Register, sources/alpha-risk-register.md
- Channel Log: Alpha - Team Channel Log (September), sources/alpha-team-channel-log-september.md
- ADR-001: decisions/ADR-001-store-readings-in-utc.md
- ADR-002: decisions/ADR-002-message-broker.md
- Issue 1: https://github.com/eraserhead21/claude-org-poc/issues/1
- Issue 3: https://github.com/eraserhead21/claude-org-poc/issues/3
- Issue 5: https://github.com/eraserhead21/claude-org-poc/issues/5
- Issue 6: https://github.com/eraserhead21/claude-org-poc/issues/6
- PR 7: https://github.com/eraserhead21/claude-org-poc/pull/7
- handler.py: src/ingest/handler.py
- backfill.py: src/ingest/backfill.py
