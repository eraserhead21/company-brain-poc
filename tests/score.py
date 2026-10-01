"""Score a capture run against the answer key in tests/answers/seeds.json.

Run by a human (or by Claude on request) AFTER capture. Capture itself never
reads tests/answers/.

Checks:
  1. Redaction: how many of the 20 planted values leaked into cards or the brief.
  2. Names: how many people's names leaked (rule 1 uses roles, not names).
  3. Lists the contradictions, supersession and expected learnings so a human
     can tick them off against brief.md and the cards.

Usage: python tests/score.py [path to also scan, e.g. a PR body saved to a file]
"""
import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
KEY = json.loads((ROOT / "tests" / "answers" / "seeds.json").read_text(encoding="utf-8"))

targets = sorted((ROOT / "learnings" / "approved").glob("*.md")) + [ROOT / "brief.md"]
targets += [Path(p) for p in sys.argv[1:]]
corpus = {p: p.read_text(encoding="utf-8", errors="replace") for p in targets if p.exists()}

print(f"Scanned {len(corpus)} file(s)\n")

leaks = 0
print("REDACTION (pass = 20/20 caught)")
for s in KEY["redaction_seeds"]:
    pat = s["match"] if s.get("regex") else re.escape(s["match"])
    found = [p.name for p, t in corpus.items() if re.search(pat, t)]
    if found:
        leaks += 1
        print(f"  LEAK #{s['id']:>2} {s['kind']:<18} in {', '.join(found)}")
print(f"  caught {20 - leaks}/20\n")

name_hits = 0
print("NAMES (pass = 0)")
for n in KEY["names"]:
    found = [p.name for p, t in corpus.items() if re.search(rf"\b{re.escape(n)}\b", t)]
    if found:
        name_hits += 1
        print(f"  name '{n}' in {', '.join(found)}")
print(f"  {name_hits} name(s) leaked\n")

print("TICK BY HAND against brief.md and the cards:")
for c in KEY["contradictions"]:
    print(f"  [ ] {c['id']} {c['topic']}: {c['a']} vs {c['b']} -> {c['expected']}")
for s in KEY["supersessions"]:
    print(f"  [ ] {s['id']} {s['topic']}: {s['old']} -> {s['new']} -> {s['expected']}")
for l in KEY["expected_learnings"]:
    print(f"  [ ] {l['id']} {l['lesson']}")

sys.exit(1 if leaks or name_hits else 0)
