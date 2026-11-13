---
id: 2026-10-20-reconcile-export-against-real-invoices-before-cutover
title: Reconcile new billing exports against real invoices before cutover
type: learning
project: alpha
date: 2026-10-20
owner_role: Team
confidence: high
sensitivity: internal
sources: [Google Drive: Alpha - Cutover Rehearsal Notes 2026-10-20]
supersedes: none
---
**Context:** Project Alpha was moving billing to a new streaming export before cutover. The old batch job handled some tariff codes through an undocumented lookup table.

**What happened:** A rehearsal run against a copy of last month's real invoices found 3 tariff codes the new export did not map. After the mapping was added, the rerun matched the invoices line for line.

**What we learned:** Reconcile a new export against real past invoices, not test data, before cutover. Undocumented business rules in the old system only show up when real data is used.
