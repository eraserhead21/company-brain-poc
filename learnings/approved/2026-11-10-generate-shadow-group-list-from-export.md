---
id: 2026-11-10-generate-shadow-group-list-from-export
title: Generate the shadow-run meter-group list from the firmware rollout export, not by hand
type: learning
project: alpha
date: 2026-11-10
owner_role: Engineer
confidence: high
sensitivity: internal
sources: [sources/alpha-meeting-notes-2026-11-10-weekly.md]
supersedes: none
---
**Context:** The shadow run compares readings only for the meter groups on its list.
**What happened:** The dry run missed 2 meter groups, because the group list for the comparison was copied by hand.
**What we learned:** Generate the meter-group list for the shadow run from the firmware rollout export. Do not copy it by hand.
