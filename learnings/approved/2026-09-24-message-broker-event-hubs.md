---
id: 2026-09-24-message-broker-event-hubs
title: Pick a managed broker when the team has no production operations experience
type: decision
project: alpha
date: 2026-09-24
owner_role: TL
confidence: high
sensitivity: internal
sources: [decisions/ADR-002-message-broker.md]
supersedes: none
---
**Context:** The pipeline needs a partitioned, durable broker for meter readings, with more load during backfill.
**What happened:** ADR-002 chose Azure Event Hubs (Standard tier, 12 partitions, keyed by meter_id). The team had no production Kafka operations experience, and the customer already ran on Azure.
**What we learned:** A managed broker removes operations risk for a small team. Its throughput limits apply per throughput unit, so the backfill must be throttled.
