# Eval answer key

1. 28 November 2026. Was 14 November. Firmware v2.3 malformed timestamps, plus the backfill now needs about 15 days.
2. Azure Event Hubs (ADR-002). Managed service, no Kafka ops experience in the team, customer already on Azure. Note: Solution Design v1 still says Kafka on AKS (conflict C2).
3. Idempotency key meter_id + UTC reading_ts, upsert on conflict.
4. Stored in UTC; local time only at the billing export (ADR-001). Avoids double counting the repeated hour.
5. About 15 days. The broker throttles near 5,000 messages per second; the one-month test ran at 3x the estimate.
6. A 7-day shadow run with under 0.1% daily mismatch between streamed and batch totals.
7. Unresolved: 90 days (Solution Design v1) vs 30 days (weekly meeting 29 Sep). A correct answer flags the conflict.
8. Meter firmware v2.3 malformed timestamps; the customer owns the fix and has no date.
9. Request customer sandbox access at kickoff; plan the backfill from a measured test; mask customer data before logging.
10. Unresolved: the channel log says one engineer, the 30 Sep status says another. A correct answer flags the conflict.
