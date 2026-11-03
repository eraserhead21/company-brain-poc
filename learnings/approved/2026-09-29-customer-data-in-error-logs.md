---
id: 2026-09-29-customer-data-in-error-logs
title: Customer data reaches error logs through raw request bodies
type: risk
project: alpha
date: 2026-09-29
owner_role: Engineer
confidence: high
sensitivity: internal
sources: [https://github.com/eraserhead21/claude-org-poc/issues/6, sources/alpha-risk-register.md]
supersedes: none
---
**Context:** Validation errors are written to the error log.
**What happened:** Error logs contain raw request bodies, which include customer details. A validation error on 29 September showed this. The masking fix is open.
**What we learned:** Mask customer fields before they are logged, not after. Check every log path that records a request body.
