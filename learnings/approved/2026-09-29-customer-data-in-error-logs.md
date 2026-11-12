---
id: 2026-09-29-customer-data-in-error-logs
title: Customer data reaches error logs until masking is in place
type: risk
project: alpha
date: 2026-09-29
owner_role: Engineer
confidence: high
sensitivity: internal
sources: [https://github.com/eraserhead21/company-brain-poc/issues/6, sources/alpha-risk-register.md]
supersedes: none
---
**Context:** The ingestion service writes validation errors to its logs.
**What happened:** The error logs held raw request bodies, which carry customer details. An example from 29 Sep appeared in a validation error. The risk register rated the impact high.
**What we learned:** Mask customer data before it is logged. The mitigation was still open when the register was last updated.
