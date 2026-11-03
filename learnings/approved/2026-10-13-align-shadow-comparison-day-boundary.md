---
id: 2026-10-13-align-shadow-comparison-day-boundary
title: Fix the shadow comparison day boundary before the run starts
type: learning
project: alpha
date: 2026-10-13
owner_role: Team
confidence: high
sensitivity: internal
sources: [sources/alpha-meeting-notes-2026-10-13-weekly.md]
supersedes: none
---
**Context:** The shadow comparison dry run checked batch totals against stream totals.
**What happened:** Batch totals used the billing local day and stream totals used the UTC day. The readings were the same, but the day boundaries differed. The mismatch alert fired on dry-run day 2.
**What we learned:** Fix the comparison window to the billing day boundary before a shadow run starts, not during it.
