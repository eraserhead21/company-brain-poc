# Capture log

Append-only. One line per run. `/capture` reads the last `cursor=` value and
reads only items changed after it.

Format: `YYYY-MM-DDTHH:MM:SSZ | <op> | cursor=<ISO time> | <counts> | <notes>`

2026-10-01T00:00:00Z | init | cursor=2026-01-01T00:00:00Z | - | Repo created. First capture reads everything.
