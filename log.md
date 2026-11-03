# Capture log

Append-only. One line per run. `/capture` reads the last `cursor=` value and
reads only items changed after it.

Format: `YYYY-MM-DDTHH:MM:SSZ | <op> | cursor=<ISO time> | <counts> | <notes>`

2026-10-01T00:00:00Z | init | cursor=2026-01-01T00:00:00Z | - | Repo created. First capture reads everything.
2026-10-01T16:44:57Z | capture | cursor=2026-10-01T16:44:57Z | drive=9 gh=6/1/3 cards=7 dropped=14 conflicts=0 superseded=2 regex_fixes=0 | ok; run via general-purpose Haiku agent (project agent not yet registered); 58.8k subagent tokens, 36 tool calls, 2m45s
2026-10-01T18:09:12Z | lint | cursor=2026-10-01T16:44:57Z | contradictions=0 stale=0 orphans=0 duplicates=0 redaction=0 | ok; conflicts missed at capture never reach the wiki, so lint cannot see them; 46.5k Haiku tokens
2026-10-01T18:09:39Z | capture | cursor=2026-10-01T18:09:39Z | drive=5(expected 1) gh=0/0/0 cards=1 dropped=0 conflicts=0 superseded=0 regex_fixes=0 | delta test: Drive filter returned 4 stale files, fixed by client-side modifiedTime check; GitHub delta ok; 59.6k Haiku tokens
2026-11-03T15:25:22Z | reset | cursor=2026-01-01T00:00:00Z | - | full re-capture for claude-vault#114: cards and brief removed on this branch, rebuilt from all sources
2026-11-03T15:25:44Z | capture | cursor=2026-11-03T15:25:44Z | drive=10 gh=6/1/5 cards=9 dropped=3 conflicts=4 superseded=7 regex_fixes=0 | ok; full rebuild for claude-vault#114; conflict rules from the run prompt now in card-extractor.md; 115.2k Haiku tokens, 40 tool calls, 2m59s; score 20/20, names 0, hand checks 11/12 (C1 retention recorded as supersession, key expects open conflict)
