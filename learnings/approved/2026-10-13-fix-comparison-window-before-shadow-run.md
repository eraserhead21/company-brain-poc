---
id: 2026-10-13-fix-comparison-window-before-shadow-run
title: Fix the shadow-run comparison window to the billing day before the run starts
type: learning
project: alpha
date: 2026-10-13
owner_role: TL
confidence: high
sensitivity: internal
sources: [sources/alpha-meeting-notes-2026-10-13-weekly.md]
supersedes: none
---
**Context:** A shadow run compares streamed totals with batch totals.
**What happened:** On day 2 of the dry run, the mismatch alert fired. Batch totals used the billing local day, and the stream comparison used the UTC day. The readings were the same, but the day boundaries differed. The team aligned both to the billing local day.
**What we learned:** Fix the comparison window to the billing day boundary before a shadow run starts, not during it.
