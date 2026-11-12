"""Save the GitHub issues and pull requests that cards cite as files in
sources/github/, so the provenance check can run with no network.

A card cites an issue by its URL. The checks map that URL to
sources/github/issue-<n>.md or sources/github/pr-<n>.md.

Usage: python scripts/snapshot_github.py issue:1 issue:3 pr:7
       python scripts/snapshot_github.py --cited     (every item a card or the brief cites)
Needs the GitHub CLI (`gh`), signed in.
"""
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sources" / "github"
CITE = re.compile(r"https://github\.com/[^/\s]+/[^/\s]+/(issues|pull)/(\d+)")


def gh(*args):
    for exe in ("gh", "C:/Program Files/GitHub CLI/gh.exe"):
        try:
            done = subprocess.run([exe, *args], capture_output=True, text=True, encoding="utf-8")
        except FileNotFoundError:
            continue
        if done.returncode != 0:
            raise SystemExit(f"gh {' '.join(args)} failed: {done.stderr.strip()}")
        return done.stdout
    raise SystemExit("GitHub CLI not found")


def cited():
    found = set()
    files = sorted((ROOT / "learnings" / "approved").glob("*.md")) + [ROOT / "brief.md", ROOT / "relations.json"]
    for f in files:
        if f.exists():
            for kind, num in CITE.findall(f.read_text(encoding="utf-8", errors="replace")):
                found.add(("issue" if kind == "issues" else "pr", int(num)))
    return sorted(found)


def snapshot(kind, num, repo):
    if kind == "issue":
        d = json.loads(gh("issue", "view", str(num), "-R", repo, "--json", "title,body,createdAt,state,comments"))
        when, label = d["createdAt"][:10], "Created"
    else:
        d = json.loads(gh("pr", "view", str(num), "-R", repo, "--json", "title,body,mergedAt,createdAt,state,comments"))
        when, label = (d.get("mergedAt") or d["createdAt"])[:10], "Merged" if d.get("mergedAt") else "Created"
    name = "ISSUE" if kind == "issue" else "PULL REQUEST"
    lines = [
        f"<!-- Snapshot of GitHub {name.lower()} #{num} in {repo}, taken {date.today().isoformat()} by scripts/snapshot_github.py.",
        "Fictional test data: every name, contact detail, secret and commercial term",
        "below is planted for the redaction test. Capture reads GitHub;",
        "the brief and cards cite the URL, and the checks read this file. -->",
        "",
        f"{name} {num}: {d['title']}",
        "",
        f"{label}: {when}. State: {d['state'].lower()}.",
        "",
        (d.get("body") or "").strip(),
    ]
    for c in d.get("comments", []):
        lines += ["", f"Comment, {c['createdAt'][:10]}:", "", (c.get("body") or "").strip()]
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{kind}-{num}.md"
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    return path


def main(args):
    repo = json.loads((ROOT / "poc-config.json").read_text(encoding="utf-8"))["repo"]
    items = cited() if "--cited" in args else []
    for a in args:
        m = re.fullmatch(r"(issue|pr):(\d+)", a)
        if m:
            items.append((m.group(1), int(m.group(2))))
    if not items:
        print(__doc__)
        return 2
    for kind, num in sorted(set(items)):
        print(f"wrote {snapshot(kind, num, repo).relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
