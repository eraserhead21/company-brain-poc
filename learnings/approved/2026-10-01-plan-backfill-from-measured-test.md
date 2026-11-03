---
id: 2026-10-01-plan-backfill-from-measured-test
title: Plan backfills from a measured test and cap below the broker throttle
type: learning
project: alpha
date: 2026-10-01
owner_role: TL
confidence: high
sensitivity: internal
sources: [https://github.com/eraserhead21/claude-org-poc/pull/7, https://github.com/eraserhead21/claude-org-poc/issues/3, sources/alpha-meeting-notes-2026-09-29-weekly.md]
supersedes: none
---
**Context:** A one-month backfill test ran through the broker before the full 18-month backfill.
**What happened:** The test ran at 3x the estimate. The broker throttled above about 5,000 messages per second. The full backfill moved from an estimated 5 days to about 15 days. PR 7 caps the publisher at 5,000 messages per second.
**What we learned:** Plan a backfill from a measured test, not an estimate. Cap the publisher below the broker throttle.
