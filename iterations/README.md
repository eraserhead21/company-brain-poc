# Iterations

One file per improvement round. Each holds the score before, what failed, the rule change, the score after, and the cost. Scores come from `tests/score.py --save`, saved in `tests/results/`.

| Round | Date | Change | Redaction | Names leaked | Hand checks | Haiku tokens |
|---|---|---|---|---|---|---|
| [1](01-baseline.md) | 2026-10-01 | Baseline | 20/20 | 0 | 8/12 | 58.8k |
| [2](02-conflict-rules.md) | 2026-11-03 | Conflict and lesson rules, `sources/` citations | 20/20 | 0 | 11/12 | 115.2k |
| [3](03-conflict-wording.md) | 2026-11-03 | Only conflicts that change an action; letter role labels | 20/20 | 0 | 11/12 | 105.2k |
| [4](04-held-out-test.md) | 2026-11-03 | None (rules frozen); new unseen sources, delta run | 6/6 held-out, 20/20 original | 0 | 7/7 held-out, 11/12 original | 92.8k |
| [5](05-provenance-and-relations.md) | 2026-11-12 | Provenance check, typed relations, checks inside capture; second set of unseen sources | 8/8 held-out, 20/20 original | 0 | 4/7 held-out (a person; a script marked 5/7), 12/12 original (script) | 123.5k rebuild, 95.5k delta |
