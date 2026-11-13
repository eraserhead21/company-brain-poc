---
id: 2026-09-30-shadow-run-mismatch-blocks-go-live
title: A shadow-run mismatch above 0.1% blocks go-live
type: risk
project: alpha
date: 2026-09-30
owner_role: PM
confidence: high
sensitivity: internal
sources: [sources/alpha-risk-register.md, sources/alpha-project-charter.md, sources/alpha-status-update-2026-10-01.md]
supersedes: none
---
**Context:** The go-live gate is a 7-day shadow run in which streamed totals match batch totals, with less than 0.1% mismatch per day.
**What happened:** The risk register rates a mismatch above 0.1% as high impact, and it would block go-live. The mitigation is a daily dashboard review from day 1 of the shadow run.
**What we learned:** A mismatch above 0.1% stops go-live, so review the comparison every day from day 1 of the shadow run.
