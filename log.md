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
2026-11-03T16:01:46Z | reset | cursor=2026-01-01T00:00:00Z | - | round 3 full re-capture for claude-vault#118: cards and brief removed on this branch, rebuilt from all sources
2026-11-03T16:02:02Z | capture | cursor=2026-11-03T16:02:02Z | drive=10 gh=6/1/3 cards=11 dropped=3 conflicts=2 superseded=8 regex_fixes=0 | ok; round 3 full rebuild for claude-vault#118 (rule 3ce478a); 105.2k Haiku tokens, 37 tool calls, 2m28s; score 20/20, names 0, hand checks 11/12 (C1 known gap)
2026-11-03T16:06:32Z | capture | cursor=2026-11-03T16:06:32Z | drive=2 gh=1/0/0 cards=2 dropped=0 conflicts=2 superseded=2 regex_fixes=0 | ok; round 4 held-out delta run for claude-vault#118, rules frozen at 3ce478a; drive_filtered_out=2; 92.8k Haiku tokens, 23 tool calls, 1m55s; held-out 6/6 redaction, 0 names, 7/7 hand checks; original key still 20/20, 0, 11/12; brief trimmed to 598 words by dropping old supersession lines
2026-11-12T14:37:42Z | reset | cursor=2026-01-01T00:00:00Z | - | round 5 full re-capture for claude-vault#134 and #135: cards and brief removed on this branch, rebuilt from all sources in staged mode
2026-11-12T14:38:00Z | capture | cursor=2026-11-12T14:38:00Z | drive=14 gh=7/1/3 cards=9 dropped=1 relations=5/4/0 regex_fixes=0 gate=0->0 | ok; round 5 rebuild attempt 1 for claude-vault#134 and #135, staged mode, rules at 4e5ecd8; 115.2k Haiku tokens, 47 tool calls, 2m36s; score 20/20, names 0, script marks 10/12 (C1 now an open conflict; no card for the kickoff access lesson or the firmware risk)
2026-11-12T14:41:37Z | reset | cursor=2026-01-01T00:00:00Z | - | round 5 full re-capture, attempt 2: cards, brief and ledger removed on this branch, rebuilt from all sources in staged mode
