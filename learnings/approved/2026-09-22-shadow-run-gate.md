---
id: 2026-09-22-shadow-run-gate
title: Define shadow-run acceptance criteria and automate daily comparison dashboard
type: decision
project: alpha
date: 2026-09-22
owner_role: PM
confidence: high
sensitivity: internal
sources: [https://docs.google.com/document/d/1vEqxpPGqlkfiIrUDz_iJ0tOPgXYZfasPFio49w7anIs/edit, https://github.com/eraserhead21/claude-org-poc/issues/4]
supersedes: none
---

**Context:** Before switching from batch to streaming, the system must run in shadow mode, comparing streaming totals against the batch baseline.

**What happened:** The project defined a 7-day shadow-run gate: streamed totals must match batch totals with less than 0.1% daily mismatch per meter group. A dashboard was built to automate this daily comparison.

**What we learned:** Establish a clear, measurable acceptance gate for shadow runs before they start. Automate the comparison dashboard so trends are visible daily from day 1. This gives early warning of systematic mismatches and builds confidence in the migration.
