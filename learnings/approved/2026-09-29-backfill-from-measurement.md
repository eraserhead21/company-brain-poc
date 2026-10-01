---
id: 2026-09-29-backfill-from-measurement
title: Measure backfill performance before committing to a full plan
type: learning
project: alpha
date: 2026-09-29
owner_role: TL
confidence: high
sensitivity: internal
sources: [https://github.com/eraserhead21/claude-org-poc/issues/3, https://github.com/eraserhead21/claude-org-poc/pull/7, https://docs.google.com/document/d/1Z037GwtrDkHF3xwjL9g0OYQ_XZmxfMKYFhPMyNNQXnQ/edit]
supersedes: none
---

**Context:** Project planned a 5-day backfill of 18 months of meter readings (about 2.1 billion records).

**What happened:** A one-month test run took 3x the estimate. The broker throttled the publisher above 5,000 msg/s. Throttling the backfill to 5k msg/s extended the full 18-month backfill from 5 days to about 15 days.

**What we learned:** Run a measured test on representative data volume before committing the full backfill plan. Adjust the plan based on observed throughput bottlenecks, not estimation. This was captured in PR #7 as a lesson for future backfills.
