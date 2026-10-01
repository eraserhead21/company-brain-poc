---
id: 2026-09-30-firmware-compatibility
title: Validate and handle malformed timestamps from meter firmware
type: risk
project: alpha
date: 2026-09-30
owner_role: TL
confidence: high
sensitivity: internal
sources: [https://github.com/eraserhead21/claude-org-poc/issues/5, https://docs.google.com/document/d/1iHWzpIVTljEkcrTaBoil-YivhQXXvYCuGXwtY1doEQ8/edit, https://docs.google.com/document/d/1Z037GwtrDkHF3xwjL9g0OYQ_XZmxfMKYFhPMyNNQXnQ/edit]
supersedes: none
---

**Context:** Meter firmware v2.3 sends malformed timestamps (e.g., 2026-13-01T25:61).

**What happened:** Timestamps are rejected and logged. The customer owns the firmware fix; no delivery date has been confirmed yet. This delayed go-live by 2 weeks while waiting for the firmware fix or for invalid readings to age out in production.

**What we learned:** Validate timestamp format at ingestion. Log rejected malformed readings for audit. Expect firmware compatibility issues in hardware sensor networks; plan for rejection and customer coordination on fixes, not automatic correction.
