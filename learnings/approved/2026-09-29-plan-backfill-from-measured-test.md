---
id: 2026-09-29-plan-backfill-from-measured-test
title: Plan a backfill from a measured test, not an estimate
type: learning
project: alpha
date: 2026-09-29
owner_role: TL
confidence: high
sensitivity: internal
sources: [sources/alpha-meeting-notes-2026-09-29-weekly.md, sources/alpha-solution-design-v1.md, https://github.com/eraserhead21/company-brain-poc/issues/3, https://github.com/eraserhead21/company-brain-poc/pull/7]
supersedes: none
---
**Context:** The design estimated the 18-month history backfill at 5 days.
**What happened:** The one-month backfill test ran at 3x the estimated time. The broker throttled the publisher above about 5,000 messages per second. The publisher was capped at 5k msg/s, and the full backfill now needs about 15 days.
**What we learned:** Plan a backfill from a measured test, not from an estimate. Re-plan the schedule from the measured rate.
