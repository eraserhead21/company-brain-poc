---
id: 2026-09-29-customer-data-in-error-logs
title: Customer data in error logs
type: risk
project: alpha
date: 2026-09-29
owner_role: Engineer
confidence: high
sensitivity: internal
sources: [sources/alpha-risk-register.md, https://github.com/eraserhead21/claude-org-poc/issues/6]
supersedes: none
---
**Context:** Error logs include raw request bodies.
**What happened:** A validation error on 29 Sep logged a request body with customer details. The mitigation, masking before logging, is still open.
**What we learned:** Mask customer details before any request body is logged.
