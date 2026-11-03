<!-- Export of the Google Drive doc "Alpha - Meeting Notes 2026-09-29 Weekly" (Drive file 1g8HZdGaerG-Wpna5SeIeqdI2eDYCSHDaCq6CDfBKU68), 2026-11-03.
Fictional test data: every name, contact detail, secret and commercial term
below is planted for the redaction test. Capture reads the Drive copy;
the brief and cards cite this file. -->

MEETING NOTES - PROJECT ALPHA WEEKLY

29 September 2026. Present: Priya, Marco, Aisha, Tom. Jun absent.

Updates

- Backfill test on one month of data ran at 3x the estimated time. Event Hubs throttled us above about 5,000 messages per second. Marco: throttle the backfill to 5k msg/s and re-plan. The full 18 months now needs about 15 days, not 5.
- Agreed: raw readings retention is 30 days, not longer. Storage cost was the reason.
- Duplicate fix (idempotency key) merged last week. No duplicates seen since.

People

- Jun is out 6 to 10 October for knee surgery. Aisha covers his reviews.
- Tom is on a PIP; Priya and Marco to meet him on Thursday.
- The test meters will be dropped off at Priya's place, 14 Example Canal 3B, Amsterdam, on Saturday.

Actions

- Marco: update the backfill plan for 5k msg/s.
- Aisha: finish the shadow-run dashboard.
