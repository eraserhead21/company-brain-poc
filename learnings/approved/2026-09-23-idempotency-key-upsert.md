---
id: 2026-09-23-idempotency-key-upsert
title: Dedupe resent meter readings with an idempotency key and upsert
type: decision
project: alpha
date: 2026-09-23
owner_role: Engineer
confidence: high
sensitivity: internal
sources: [https://github.com/eraserhead21/claude-org-poc/issues/1, src/ingest/handler.py]
supersedes: none
---
**Context:** Meters resend the last batch of readings after a network drop. That double counted billing totals in the sandbox.
**What happened:** The key is meter ID plus UTC reading time. The readings store upserts on conflict. The sandbox showed no duplicates from 23 Sep.
**What we learned:** Give every reading a key built from the meter and the UTC reading time. Upsert on that key, so a resent reading overwrites and does not add.
