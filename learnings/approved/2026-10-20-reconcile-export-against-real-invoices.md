---
id: 2026-10-20-reconcile-export-against-real-invoices
title: Reconcile a new billing export against last month's real invoices before cutover
type: learning
project: alpha
date: 2026-10-20
owner_role: Team
confidence: high
sensitivity: internal
sources: [sources/alpha-cutover-rehearsal-notes-2026-10-20.md]
supersedes: none
---
**Context:** The new streaming billing export had to replace the batch job before cutover.
**What happened:** The rehearsal ran the new export on a copy of September's real invoices. It found 3 tariff codes (night rate, weekend rate, export credit) that the new export did not map. The old batch job handled them in an undocumented lookup table. After the 3 codes were added, the rerun matched September's invoices line for line.
**What we learned:** Reconcile a new export against last month's real invoices before cutover, not against test data. Undocumented business rules live in the old system and appear only with real data.
