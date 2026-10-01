# Project Alpha brief

## Status

**Overall: AMBER.** Go-live pushed to 28 November (was 14 November) due to meter firmware compatibility issues and backfill performance reality. The streaming ingestion pipeline is being built; core components are working; shadow-run gate and go-live gate both defined.

## Key dates

| Event | Original | Current |
|---|---|---|
| Design sign-off | 19 Sep | ✓ Done 19 Sep |
| Backfill test (1 month) | — | ✓ Done, revealed throttle at 5k msg/s |
| Backfill full (18 months) | 17 Oct (5 days) | ~15 Nov (15 days at 5k msg/s cap) |
| Shadow run | 3 Nov | 17 Nov (7-day gate: <0.1% daily mismatch per meter group) |
| Go-live | 14 Nov | 28 Nov |

## Decisions

**UTC storage (ADR-001).** Convert all meter timestamps to UTC at ingestion; store UTC only. Convert to local time only in billing export. Prevents double-counting during daylight-saving transitions (25 Oct) and simplifies idempotency and cross-timezone reporting.

**Message broker (ADR-002).** Azure Event Hubs, Standard tier, 12 partitions keyed by meter ID. Chosen for managed operations (team has no Kafka production experience) and faster access reviews (customer already on Azure).

**Meter deduplication.** Idempotency key: meter ID + UTC reading timestamp, upsert-on-conflict in PostgreSQL. Meters resend after network drops; this approach eliminated duplicates as of 23 September.

**Backfill throttling.** Cap backfill publisher at 5,000 msg/s. A one-month test revealed broker throttling above this rate; estimated throughput is 3x slower than initial estimate. Full 18-month backfill now planned at 15 days.

**Raw readings retention.** 30 days (originally 90). Reduced for storage cost and log retention policy.

## Open risks

**Firmware v2.3 malformed timestamps (HIGH).** Some meters send invalid timestamps (e.g., 2026-13-01T25:61). Currently rejected and logged. Customer owns the firmware fix; no date confirmed. Delays go-live by ~6 weeks pending fix or aging out of invalid readings in production.

**Customer data in error logs (HIGH).** Validation failure logs include raw request bodies with customer details. Mitigation in progress: mask sensitive fields before logging. Must close before production.

**Shadow-run mismatch above 0.1% (HIGH).** Would block go-live. Mitigation: daily dashboard review starting day 1 of shadow run.

**Backfill duration (MEDIUM).** Extended from 5 to 15 days. Reduces window for correcting issues before shadow run.

## Sources

- **Drive:** Alpha - Project Charter (2026-09-08), Alpha - Solution Design v1 (2026-09-10), Alpha - Meeting Notes 2026-09-15 Kickoff, Alpha - Meeting Notes 2026-09-29 Weekly, Alpha - Status Update 2026-09-22, Alpha - Status Update 2026-09-30, Alpha - Risk Register (2026-09-30), Alpha - Team Channel Log (September), Alpha - Onboarding Notes
- **GitHub:** [Issues #1–6](https://github.com/eraserhead21/claude-org-poc/issues), [PR #7](https://github.com/eraserhead21/claude-org-poc/pull/7)
- **Repo:** [decisions/ADR-001](decisions/ADR-001-store-readings-in-utc.md), [decisions/ADR-002](decisions/ADR-002-message-broker.md), [docs/architecture.md](docs/architecture.md)
