---
id: 2026-09-29-backfill-plan-from-measured-test
title: Plan the backfill from a measured test, not an estimate
type: learning
project: alpha
date: 2026-09-29
owner_role: TL
confidence: high
sensitivity: internal
sources: [sources/alpha-meeting-notes-2026-09-29-weekly.md, https://github.com/eraserhead21/claude-org-poc/issues/3, https://github.com/eraserhead21/claude-org-poc/pull/7]
supersedes: none
---
**Context:** The 18-month backfill was estimated at 5 days in the design.
**What happened:** A one-month test ran at 3 times the estimate. The broker throttled above about 5,000 messages per second. The publisher is now capped at 5,000 messages per second, and the full backfill is planned at about 15 days.
**What we learned:** Plan a backfill from a measured test run. Cap the publish rate at the limit the test found.
