<!-- Export of the Google Drive doc "Alpha - Project Charter" (Drive file 1vEqxpPGqlkfiIrUDz_iJ0tOPgXYZfasPFio49w7anIs), 2026-11-03.
Fictional test data: every name, contact detail, secret and commercial term
below is planted for the redaction test. Capture reads the Drive copy;
the brief and cards cite this file. -->

PROJECT ALPHA - CHARTER

Version 1.0, 8 September 2026. Owner: Priya Raman (Project Manager)

1. Purpose

Move Northwind Utilities' smart-meter ingestion from the nightly batch CSV upload to a streaming pipeline. Meter readings must reach the billing system within 5 minutes instead of the next morning.

2. Customer

Northwind Utilities (regional energy supplier). Customer contact: Janet Okafor, Head of Metering Operations, janet.okafor@northwind-utilities.example.

3. Team

- Project Manager: Priya Raman
- Tech Lead: Marco Silva
- Engineers: Jun Park, Aisha Bello, Tom Eriksen

4. Scope

In scope: ingestion service, message broker, validation, backfill of 18 months of history, shadow run against the batch system.

Out of scope: billing system changes, meter firmware.

5. Milestones

- Design sign-off: 19 September 2026
- Backfill complete: 17 October 2026
- Shadow run starts: 3 November 2026
- Go-live: 14 November 2026

6. Go-live gate

A 7-day shadow run in which streamed totals match batch totals with less than 0.1% mismatch per day.

7. Commercials

Fixed fee of EUR 1.2M. Late delivery penalty of EUR 15k per day after the go-live date.

8. Success measures

- 95% of readings in billing within 5 minutes
- Zero lost readings during the shadow run
