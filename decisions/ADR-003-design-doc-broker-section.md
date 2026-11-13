# ADR-003: Broker section of Solution Design v1

- Status: Accepted
- Date: 2026-10-28
- Deciders: Tech Lead, Project Manager

## Context

Solution Design v1 names a self-run Kafka cluster as the message broker. ADR-002
chose Azure Event Hubs. New team members read the design document and asked
which one is right.

## Decision

Azure Event Hubs is the message broker. This record replaces section 2 (Message broker) of Solution Design v1.

## Consequences

- Section 2 of Solution Design v1 is out of date. The rest of the document stands.
