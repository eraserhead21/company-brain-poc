"""Stage the capture inputs from the repo, for a capture run with no Drive
and no GitHub access ("staged mode").

It copies every source that changed after the cursor into .capture-input/,
without the export comment at the top of each file. That comment says the
data is planted for a redaction test, which the live Drive document does not
say. It also writes .capture-input/MANIFEST.md: one line per staged file,
with the citation that cards and the brief must use for it.

Staged folders: sources/ (Drive exports), sources/github/ (issue and PR
snapshots), decisions/ and docs/. Nothing under tests/ is ever staged.

"Changed after the cursor" means the file's last commit is later than the
cursor, or the file has changes that are not committed.

Usage: python scripts/stage_sources.py --since 2026-01-01T00:00:00Z
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / ".capture-input"
HEADER = re.compile(r"\A\s*<!--.*?-->\s*", re.S)
FOLDERS = (("sources", "*.md", "Drive document"), ("sources/github", "*.md", "GitHub item"),
           ("decisions", "*.md", "decision record"), ("docs", "*.md", "repo document"))


def git(*args):
    done = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, encoding="utf-8")
    return done.stdout.strip() if done.returncode == 0 else ""


def changed_at(rel):
    """Time of the last change: now for uncommitted work, else the last commit."""
    if git("status", "--porcelain", "--", rel):
        return datetime.now(timezone.utc)
    stamp = git("log", "-1", "--format=%cI", "--", rel)
    return datetime.fromisoformat(stamp) if stamp else datetime.now(timezone.utc)


def citation(rel, repo):
    m = re.fullmatch(r"sources/github/(issue|pr)-(\d+)\.md", rel)
    if m:
        return f"https://github.com/{repo}/{'issues' if m.group(1) == 'issue' else 'pull'}/{m.group(2)}"
    return rel


def title_of(text, rel):
    for line in text.splitlines():
        if line.strip():
            return line.strip().lstrip("# ").strip()
    return rel


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--since", required=True, help="the capture cursor, ISO time")
    args = ap.parse_args(argv)
    since = datetime.fromisoformat(args.since.replace("Z", "+00:00"))
    if since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    repo = json.loads((ROOT / "poc-config.json").read_text(encoding="utf-8"))["repo"]

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    rows, skipped = [], 0
    for folder, pattern, kind in FOLDERS:
        for f in sorted((ROOT / folder).glob(pattern)):
            rel = f.relative_to(ROOT).as_posix()
            if changed_at(rel) <= since:
                skipped += 1
                continue
            text = HEADER.sub("", f.read_text(encoding="utf-8", errors="replace"), count=1)
            target = OUT / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8", newline="\n")
            rows.append((f".capture-input/{rel}", kind, title_of(text, rel), citation(rel, repo)))
    lines = ["# Capture input", "",
             f"Staged {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} for cursor {args.since}.",
             "Read every file in this list. Cite each one with the text in its last column.", "",
             "| File to read | Kind | Title | Cite as |", "|---|---|---|---|"]
    lines += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows]
    (OUT / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    by_kind = {}
    for _, kind, _, _ in rows:
        by_kind[kind] = by_kind.get(kind, 0) + 1
    summary = ", ".join(f"{n} {k}(s)" for k, n in by_kind.items()) or "nothing"
    print(f"staged {len(rows)} file(s): {summary}; {skipped} not changed since the cursor")
    return 0


if __name__ == "__main__":
    sys.exit(main())
