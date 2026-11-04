---
id: 2026-10-20-reconcile-export-against-real-invoices-before-cutover
title: Reconcile new billing exports against real invoices before cutover
type: learning
project: alpha
date: 2026-10-20
owner_role: TL
confidence: high
sensitivity: internal
sources: [Google Drive: Alpha - Cutover Rehearsal Notes 2026-10-20]
supersedes: none
---
**Context:** A new streaming billing export was replacing an old batch job before cutover. The old job held business rules in an undocumented lookup table.

**What happened:** A rehearsal run against a copy of last month's real invoices found three tariff codes the new export did not map. Adding them made the rerun match the invoices line for line.

**What we learned:** Reconcile a new export against real past invoices, not test data, before cutover. Undocumented business rules in the old system only surface against real data.
