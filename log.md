# Capture log

Append-only. One line per run. `/capture` reads the last `cursor=` value and
reads only items changed after it.

Format: `YYYY-MM-DDTHH:MM:SSZ | <op> | cursor=<ISO time> | <counts> | <notes>`

2026-10-01T00:00:00Z | init | cursor=2026-01-01T00:00:00Z | - | Repo created. First capture reads everything.
2026-10-01T16:44:57Z | capture | cursor=2026-10-01T16:44:57Z | drive=9 gh=6/1/3 cards=7 dropped=14 conflicts=0 superseded=2 regex_fixes=0 | ok; run via general-purpose Haiku agent (project agent not yet registered); 58.8k subagent tokens, 36 tool calls, 2m45s
2026-10-01T18:09:12Z | lint | cursor=2026-10-01T16:44:57Z | contradictions=0 stale=0 orphans=0 duplicates=0 redaction=0 | ok; conflicts missed at capture never reach the wiki, so lint cannot see them; 46.5k Haiku tokens
