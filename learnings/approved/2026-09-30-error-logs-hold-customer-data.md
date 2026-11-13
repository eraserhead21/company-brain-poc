---
id: 2026-09-30-error-logs-hold-customer-data
title: Error logs carry raw request bodies with customer data, so mask before logging
type: risk
project: alpha
date: 2026-09-30
owner_role: Engineer
confidence: high
sensitivity: internal
sources: [sources/alpha-risk-register.md, https://github.com/eraserhead21/company-brain-poc/issues/6]
supersedes: none
---
**Context:** Error logs include raw request bodies.
**What happened:** On 29 Sep, a validation error logged customer details. The risk has high impact and is open. The mitigation is to mask the data before logging.
**What we learned:** Mask customer data before any error is logged. Until the mask is in place, error logs hold customer data.
