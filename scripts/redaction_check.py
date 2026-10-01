"""Deterministic redaction backstop for learning cards and the brief.

Generic patterns only. It does not know the planted test values, so it is a
fair second line behind the LLM redaction step, not a copy of the answer key.

Usage: python scripts/redaction_check.py <file or folder> [...]
Exit code 1 when any hit is found.
"""
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PATTERNS = {
    "email": r"[\w.+-]+@[\w-]+\.[\w.-]+",
    "phone": r"(?<!\w)\+?\d[\d \-]{8,}\d(?!\w)",
    "money": r"[€$£]\s?\d[\d.,]*\s?[kKmM]?",
    "secret_word": r"(?i)\b(pass(word)?|pwd|api[_ -]?key|token|secret|vpn|wi-?fi|sftp)\b\s*[:=]",
    "dob": r"(?i)\b(dob|date of birth|born)\b",
    "account_id": r"\b[A-Z]{2,}-ACCT-\d+\b",
    "hr_words": r"(?i)\b(salary|raise|pip|performance improvement|sick|surgery|medical)\b",
    "commercial": r"(?i)\b(margin|penalt(y|ies)|contract value|dispute|switch(ing)? vendor)\b",
}


def scan(path: Path):
    hits = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith(("sources:", "- http", "http")):
            continue
        for name, pat in PATTERNS.items():
            for m in re.finditer(pat, line):
                hits.append((path, lineno, name, m.group(0)))
    return hits


def main(args):
    files = []
    for a in args:
        p = Path(a)
        files += sorted(p.rglob("*.md")) if p.is_dir() else [p]
    hits = [h for f in files if f.exists() for h in scan(f)]
    for path, lineno, name, match in hits:
        print(f"{path}:{lineno}: {name}: {match}")
    print(f"{len(hits)} hit(s) in {len(files)} file(s)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["learnings/approved", "brief.md"]))
