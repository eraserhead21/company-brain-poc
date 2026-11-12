---
id: 2026-10-13-align-comparison-window-to-billing-day
title: Fix the shadow-run comparison window to the billing day before the run starts
type: learning
project: alpha
date: 2026-10-13
owner_role: Engineer
confidence: high
sensitivity: internal
sources: [sources/alpha-meeting-notes-2026-10-13-weekly.md, sources/alpha-status-update-2026-10-15.md]
supersedes: none
---
**Context:** The shadow comparison checks streamed totals against batch totals for each day. The dry run started on 12 October.
**What happened:** On day 2 of the dry run the mismatch alert fired. Batch totals use the billing local day, 00:00 to 00:00. The stream comparison used the UTC day. The same readings fell into different days. Both were aligned to the billing local day.
**What we learned:** Fix the comparison window to the billing day boundary before a shadow run starts, not during it.
