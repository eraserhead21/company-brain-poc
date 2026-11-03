---
id: 2026-09-30-firmware-v23-malformed-timestamps
title: Meter firmware v2.3 sends malformed timestamps
type: risk
project: alpha
date: 2026-09-30
owner_role: TL
confidence: high
sensitivity: internal
sources: [https://github.com/eraserhead21/claude-org-poc/issues/5, sources/alpha-risk-register.md, sources/alpha-status-update-2026-09-30.md]
supersedes: none
---
**Context:** Some meters run firmware v2.3. Their timestamps are invalid, for example 2026-13-01.
**What happened:** Confirmed on 30 September. Malformed readings are rejected and logged. The customer owns the firmware fix, which Northwind confirmed for v2.4 on 20 October.
**What we learned:** A fix owned by the customer or vendor can block go-live. Reject and log bad input meanwhile, and track the fix date as a dependency.
