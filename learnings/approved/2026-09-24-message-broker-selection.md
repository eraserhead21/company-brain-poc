---
id: 2026-09-24-message-broker-selection
title: Managed message broker preferred over self-hosted when operational expertise is lacking
type: decision
project: alpha
date: 2026-09-24
owner_role: TL
confidence: high
sensitivity: internal
sources: [decisions/ADR-002-message-broker.md]
supersedes: none
---

**Context:** The streaming pipeline requires a partitioned, durable broker handling about 2,000 msg/s steady state and higher during backfill.

**What happened:** Team evaluated Kafka versus managed Event Hubs. No team member had production Kafka operations experience.

**What we learned:** Use a managed message broker (Azure Event Hubs, Standard tier, 12 partitions keyed by meter ID) when the team lacks operations expertise for self-hosted alternatives. Trade-off: throughput is metered and backfill must be throttled, but reduces operational burden and speeds vendor access reviews when the customer already uses the same cloud.
