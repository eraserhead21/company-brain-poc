---
id: 2026-09-30-firmware-v23-malformed-timestamps
title: Meter firmware v2.3 sends malformed timestamps until the customer ships a fix
type: risk
project: alpha
date: 2026-09-30
owner_role: TL
confidence: high
sensitivity: internal
sources: [sources/alpha-risk-register.md, https://github.com/eraserhead21/company-brain-poc/issues/5, sources/alpha-status-update-2026-10-01.md, sources/alpha-meeting-notes-2026-10-13-weekly.md]
supersedes: none
---
**Context:** Some meters on firmware v2.3 send malformed timestamps, for example 2026-13-01T25:61. The customer owns the firmware fix.
**What happened:** The risk is confirmed, with high impact. Malformed readings are rejected and logged. The v2.4 fix was due on 20 October, and its rollout slipped to 27 October.
**What we learned:** Readings from v2.3 meters are rejected until the firmware is upgraded. Hold v2.3 meter groups out of the shadow run, and measure the mismatch gate on upgraded groups only.
