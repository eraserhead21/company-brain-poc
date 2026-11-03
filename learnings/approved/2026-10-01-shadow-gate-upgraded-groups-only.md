---
id: 2026-10-01-shadow-gate-upgraded-groups-only
title: Measure the shadow-run gate on upgraded meter groups only
type: decision
project: alpha
date: 2026-10-01
owner_role: PM
confidence: high
sensitivity: internal
sources: [sources/alpha-status-update-2026-10-01.md, sources/alpha-project-charter.md]
supersedes: none
---
**Context:** The charter gate needs under 0.1% daily mismatch over a 7-day shadow run, with no scope limit on meter groups.
**What happened:** Meter groups on firmware v2.3 are held out of the shadow run until they upgrade. The gate is measured on upgraded groups only.
**What we learned:** When a device defect blocks part of the test population, exclude that population explicitly and record the changed gate scope.
