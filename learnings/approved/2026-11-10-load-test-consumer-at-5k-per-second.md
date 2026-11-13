---
id: 2026-11-10-load-test-consumer-at-5k-per-second
title: Load-test the consumer at 5k msg/s for one hour and record any lag
type: learning
project: alpha
date: 2026-11-10
owner_role: Engineer
confidence: medium
sensitivity: internal
sources: [sources/alpha-meeting-notes-2026-11-10-weekly.md]
supersedes: none
---
**Context:** Before the shadow run, the team tested how the consumer keeps up under sustained load.
**What happened:** A load test drained 5k msg/s for one hour with no lag.
**What we learned:** Test the consumer at the target rate for a full hour, and record any lag. This test showed none at 5k msg/s.
