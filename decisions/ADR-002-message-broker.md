# ADR-002: Message broker

- Status: Accepted
- Date: 2026-09-24
- Deciders: Tech Lead, Project Manager

## Context

The pipeline needs a partitioned, durable message broker for meter readings,
about 2,000 messages per second at peak in steady state, more during backfill.

## Decision

Use Azure Event Hubs (Standard tier, 12 partitions, keyed by `meter_id`).

## Reasons

- Managed service. The team has no one with production Kafka operations experience.
- Northwind already runs on Azure, so networking and access reviews are faster.

## Consequences

- Throughput limits per throughput unit apply. Backfill must be throttled.
- Kafka-protocol clients still work through the Event Hubs Kafka endpoint.
