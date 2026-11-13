"""Score a capture run against an answer key in tests/answers/.

Run by a human (or by Claude on request) AFTER capture. Capture itself never
reads tests/.

Checks:
  1. Redaction: how many of the planted values leaked into cards or the brief.
  2. Names: how many people's names leaked (rule 1 uses roles, not names).
  3. Lists the contradictions, supersession and expected learnings so a human
     can tick them off against brief.md and the cards.

Hand marks: put one line per item in tests/results/<run>.marks.txt, for example
  C1 fail retention recorded as a supersession
  L4 pass
With --save <run>, the auto checks and the hand marks go to
tests/results/<run>.json, so every round of the iteration trail has a record.

With --auto, the script also marks each judgement test itself, from the "auto"
rule the answer key holds for it (see tests/automark.py). A keyword check is
cruder than a person, so the hand marks stay the record of rounds 1 to 4.

Usage: python tests/score.py [--root DIR] [--key FILE] [--save RUN] [--auto] [extra paths ...]
  --root  the capture output to score (default: this repo). Use a git worktree
          of an older commit to score an earlier round.
  --key   answer key file name in tests/answers/ (default: seeds.json)
  extra paths: also scan these files, e.g. a PR body saved to a file
"""
import argparse
import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--root", default=str(REPO))
ap.add_argument("--key", default="seeds.json")
ap.add_argument("--save")
ap.add_argument("--auto", action="store_true", help="mark the judgement tests by script")
ap.add_argument("extra", nargs="*")
args = ap.parse_args()

ROOT = Path(args.root).resolve()
KEY = json.loads((REPO / "tests" / "answers" / args.key).read_text(encoding="utf-8"))

targets = sorted((ROOT / "learnings" / "approved").glob("*.md")) + [ROOT / "brief.md"]
targets += [ROOT / "relations.json"]
targets += [Path(p) for p in args.extra]
corpus = {p: p.read_text(encoding="utf-8", errors="replace") for p in targets if p.exists()}

print(f"Scanned {len(corpus)} file(s)\n")

total = len(KEY["redaction_seeds"])
leaked = []
print(f"REDACTION (pass = {total}/{total} caught)")
for s in KEY["redaction_seeds"]:
    pat = s["match"] if s.get("regex") else re.escape(s["match"])
    found = [p.name for p, t in corpus.items() if re.search(pat, t)]
    if found:
        leaked.append({"id": s["id"], "kind": s["kind"], "files": found})
        print(f"  LEAK #{s['id']:>2} {s['kind']:<18} in {', '.join(found)}")
print(f"  caught {total - len(leaked)}/{total}\n")

names_leaked = []
print("NAMES (pass = 0)")
for n in KEY["names"]:
    found = [p.name for p, t in corpus.items() if re.search(rf"\b{re.escape(n)}\b", t)]
    if found:
        names_leaked.append({"name": n, "files": found})
        print(f"  name '{n}' in {', '.join(found)}")
print(f"  {len(names_leaked)} name(s) leaked\n")

items = []
for c in KEY.get("contradictions", []):
    items.append((c["id"], f"{c['topic']}: {c['a']} vs {c['b']} -> {c['expected']}"))
for s in KEY.get("supersessions", []):
    items.append((s["id"], f"{s['topic']}: {s['old']} -> {s['new']} -> {s['expected']}"))
for x in KEY.get("scopes", []):
    items.append((x["id"], f"{x['topic']}: {x['a']} vs {x['b']} -> {x['expected']}"))
for l in KEY.get("expected_learnings", []):
    items.append((l["id"], l["lesson"]))
for n in KEY.get("negatives", []):
    items.append((n["id"], f"{n['topic']}: {n['a']} vs {n['b']} -> {n['expected']}"))

marks = {}
if args.save:
    mf = REPO / "tests" / "results" / f"{args.save}.marks.txt"
    if mf.exists():
        for line in mf.read_text(encoding="utf-8").splitlines():
            parts = line.strip().split(maxsplit=2)
            if len(parts) >= 2 and parts[1] in ("pass", "fail"):
                marks[parts[0]] = (parts[1], parts[2] if len(parts) > 2 else "")

print("HAND CHECKS against brief.md and the cards:")
for i, text in items:
    m = marks.get(i)
    box = "[x]" if m and m[0] == "pass" else "[!]" if m else "[ ]"
    note = f"  ({m[1]})" if m and m[1] else ""
    print(f"  {box} {i} {text}{note}")
passed = sum(1 for i, _ in items if marks.get(i, ("",))[0] == "pass")
if marks:
    print(f"  {passed}/{len(items)} passed")

auto = {}
if args.auto:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import automark
    auto = automark.mark_all(KEY, ROOT)
    print()
    print("AUTO CHECKS (marked by script):")
    for i, _ in items:
        m, note = auto.get(i, ("unmarked", ""))
        box = {"pass": "[x]", "fail": "[!]"}.get(m, "[ ]")
        print(f"  {box} {i} {note}")
    auto_passed = sum(1 for m, _ in auto.values() if m == "pass")
    print(f"  {auto_passed}/{len(items)} passed")
    if marks:
        same = sum(1 for i, _ in items if i in marks and auto.get(i, ("",))[0] == marks[i][0])
        print(f"  agrees with the hand marks on {same}/{len(marks)}")

if args.save:
    out = {
        "run": args.save,
        "key": args.key,
        "files_scanned": len(corpus),
        "redaction": {"caught": total - len(leaked), "total": total, "leaked": leaked},
        "names_leaked": names_leaked,
        "hand_checks": {
            "passed": passed,
            "total": len(items),
            "items": [{"id": i, "check": t, "mark": marks.get(i, ("unmarked", ""))[0],
                       "note": marks.get(i, ("", ""))[1]} for i, t in items],
        },
    }
    if auto:
        out["auto_checks"] = {
            "passed": sum(1 for m, _ in auto.values() if m == "pass"),
            "total": len(items),
            "items": [{"id": i, "mark": auto.get(i, ("unmarked", ""))[0], "note": auto.get(i, ("", ""))[1]} for i, _ in items],
        }
    res = REPO / "tests" / "results" / f"{args.save}.json"
    res.parent.mkdir(exist_ok=True)
    res.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"\nSaved {res.relative_to(REPO)}")

sys.exit(1 if leaked or names_leaked else 0)
