---
id: 2026-09-24-event-hubs-broker
title: Use Azure Event Hubs as the reading broker
type: decision
project: alpha
date: 2026-09-24
owner_role: TL
confidence: high
sensitivity: internal
sources: [decisions/ADR-002-message-broker.md, docs/architecture.md]
supersedes: none
---
**Context:** The pipeline needs a partitioned, durable broker for meter readings. Peak steady-state load is about 2,000 messages per second, with more during backfill.
**What happened:** ADR-002 chose Azure Event Hubs, Standard tier, 12 partitions keyed by meter ID. The team has no Kafka operations experience, and the customer already runs on Azure.
**What we learned:** The managed broker limits throughput per unit, so the backfill must be throttled.
