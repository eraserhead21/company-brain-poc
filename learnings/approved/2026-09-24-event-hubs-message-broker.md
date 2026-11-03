---
id: 2026-09-24-event-hubs-message-broker
title: Use Azure Event Hubs as the message broker
type: decision
project: alpha
date: 2026-09-24
owner_role: TL
confidence: medium
sensitivity: internal
sources: [decisions/ADR-002-message-broker.md, sources/alpha-solution-design-v1.md]
supersedes: none
---
**Context:** The pipeline needs a partitioned, durable broker for about 2,000 messages per second at peak, more during backfill.
**What happened:** ADR-002 chose Azure Event Hubs Standard, 12 partitions keyed by meter_id. Solution Design v1 names Kafka on AKS. The ADR does not say it replaces the design doc.
**What we learned:** The team chose a managed broker because it had no Kafka operations experience and the customer runs on Azure. Throughput units limit the rate, so backfill must be throttled.
