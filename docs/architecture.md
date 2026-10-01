# Project Alpha architecture (repo copy)

Short engineering view. The full solution design lives in the project Drive
folder ("Alpha - Solution Design v1").

```
head-end --HTTPS--> ingest service --> broker --> validator --> readings store --> billing export
```

- Ingest: `src/ingest/handler.py`. Normalises timestamps to UTC (ADR-001) and
  builds the idempotency key.
- Broker: see ADR-002.
- Readings store: PostgreSQL, upsert on the idempotency key.
