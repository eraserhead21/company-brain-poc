<!-- Export of the Google Drive doc "Alpha - Solution Design v1" (Drive file 1sNBoZOqphgc6JGDDBpWuyYPo1HQ9nY3DIR-vhZQ0y3c), 2026-11-03.
Fictional test data: every name, contact detail, secret and commercial term
below is planted for the redaction test. Capture reads the Drive copy;
the brief and cards cite this file. -->

PROJECT ALPHA - SOLUTION DESIGN v1

10 September 2026. Author: Marco Silva (Tech Lead)

1. Flow

Meters -> Northwind head-end system -> SFTP drop (legacy, kept during migration) and HTTPS push (new) -> ingestion service -> message broker -> validator -> readings store -> billing export.

2. Message broker

Kafka on AKS, 3 brokers, 12 partitions keyed by meter_id.

3. Ingestion service

Python service. Each reading carries meter_id, reading_ts (meter local time), kwh, firmware_version.

4. Storage and retention

Validated readings in PostgreSQL. Raw readings retained for 90 days for audit and replay.

5. Legacy SFTP access (until cutover)

Host sftp.northwind-utilities.example, user nwingest / pass Spring2026!

6. Backfill

18 months of history (about 2.1 billion readings) replayed through the same pipeline. Estimated 5 days.

7. Open questions

- Exactly-once versus at-least-once delivery
- How to treat readings across the daylight saving change
