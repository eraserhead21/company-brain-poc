---
id: 2026-09-24-event-hubs-for-message-broker
title: Use Azure Event Hubs as the message broker for meter readings
type: decision
project: alpha
date: 2026-09-24
owner_role: TL
confidence: high
sensitivity: internal
sources: [decisions/ADR-002-message-broker.md]
supersedes: none
---
**Context:** The pipeline needs a partitioned, durable message broker for meter readings, about 2,000 messages per second at peak in steady state, and more during backfill.
**What happened:** The team chose Azure Event Hubs (Standard tier, 12 partitions, keyed by meter_id). The team had no one with production Kafka operations experience, and the customer already runs on Azure.
**What we learned:** A managed broker suits a team without Kafka operations experience. Throughput limits apply per throughput unit, so backfill must be throttled.
