---
id: 2026-09-30-firmware-v23-malformed-timestamps
title: Meter firmware v2.3 sends malformed timestamps
type: risk
project: alpha
date: 2026-09-30
owner_role: TL
confidence: high
sensitivity: internal
sources: [sources/alpha-risk-register.md, https://github.com/eraserhead21/claude-org-poc/issues/5, sources/alpha-status-update-2026-09-30.md, sources/alpha-status-update-2026-10-01.md, sources/alpha-team-channel-log-september.md]
supersedes: none
---
**Context:** Some meters on firmware v2.3 send timestamps such as 2026-13-01. The customer owns the firmware fix.
**What happened:** Malformed readings are rejected and logged. Go-live moved from 14 Nov to 28 Nov 2026. The customer confirmed the v2.4 fix ships on 20 Oct 2026. Meter groups on v2.3 are held out of the shadow run.
**What we learned:** A fix owned by the customer sets the project date. Track its date as a dependency and plan a rejection path until it ships.
