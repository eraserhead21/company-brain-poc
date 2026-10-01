---
id: 2026-09-29-customer-data-in-logs
title: Mask customer details from error logs in validation failures
type: risk
project: alpha
date: 2026-09-29
owner_role: Engineer
confidence: high
sensitivity: internal
sources: [https://github.com/eraserhead21/claude-org-poc/issues/6, https://docs.google.com/document/d/1iHWzpIVTljEkcrTaBoil-YivhQXXvYCuGXwtY1doEQ8/edit]
supersedes: none
---

**Context:** The readings ingestion service includes raw request bodies in error logs.

**What happened:** Validation failures logged customer details, including addresses, creating a data-handling risk.

**What we learned:** Mask sensitive fields before logging request bodies. Include only the error reason and idempotent message identifiers (meter ID, timestamp) in error logs, not raw payloads. This is a high-impact risk that must be closed before production.
