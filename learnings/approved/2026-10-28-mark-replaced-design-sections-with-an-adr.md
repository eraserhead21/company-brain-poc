---
id: 2026-10-28-mark-replaced-design-sections-with-an-adr
title: When an ADR replaces a design section, name the section and mark it out of date
type: learning
project: alpha
date: 2026-10-28
owner_role: Team
confidence: high
sensitivity: internal
sources: [decisions/ADR-003-design-doc-broker-section.md]
supersedes: none
---
**Context:** Solution Design v1 named a self-run Kafka cluster as the message broker. ADR-002 chose Azure Event Hubs.
**What happened:** New team members read the design document and asked which broker was right. ADR-003 recorded that Event Hubs replaces the broker section of Solution Design v1.
**What we learned:** When an ADR replaces a section of a design document, name the replaced section in the ADR and mark that section out of date in the document.
