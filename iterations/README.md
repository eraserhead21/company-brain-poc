# Iterations

One file per improvement round. Each holds the score before, what failed, the rule change, the score after, and the cost. Scores come from `tests/score.py --save`, saved in `tests/results/`.

| Round | Date | Change | Redaction | Names leaked | Hand checks | Haiku tokens |
|---|---|---|---|---|---|---|
| [1](01-baseline.md) | 2026-10-01 | Baseline | 20/20 | 0 | 8/12 | 58.8k |
| [2](02-conflict-rules.md) | 2026-11-03 | Conflict and lesson rules, `sources/` citations | 20/20 | 0 | 11/12 | 115.2k |
| [3](03-conflict-wording.md) | 2026-11-03 | Only conflicts that change an action; letter role labels | 20/20 | 0 | 11/12 | 105.2k |
