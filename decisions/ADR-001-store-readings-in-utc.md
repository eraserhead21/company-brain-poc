# ADR-001: Store all readings in UTC

- Status: Accepted
- Date: 2026-09-22
- Deciders: Tech Lead, Engineers

## Context

Meters report `reading_ts` in meter local time. On the daylight-saving change
(25 October 2026), local times between 02:00 and 03:00 occur twice. Storing local
time double-counts that hour.

## Decision

Convert `reading_ts` to UTC at ingestion. Store UTC only. Convert to local time
only in the billing export.

## Consequences

- No double counting across DST changes.
- The idempotency key uses the UTC timestamp.
- Any report that shows local time must convert explicitly.
