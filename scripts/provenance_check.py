"""Provenance check: trace every fact in a card or the brief to a cited source.

For each learning card and each fact line in brief.md the check:
  1. resolves every citation to a file under the source folders;
  2. pulls out the checkable items in the claim: numbers with their unit,
     dates, times, versions, identifiers and quantity words;
  3. fails the claim if no cited source holds an item;
  4. lists the words that no cited source holds, for a person to review.

It has no model and no network. It stores pointers (file and line), never
source text, so its output cannot leak what redaction removed. It never
opens tests/.

What it cannot see: meaning. A claim that reverses a source and reuses its
words passes. So does a wrong number that the source also holds.

Usage: python scripts/provenance_check.py [--root DIR] [--trace] [--json FILE] [paths ...]
  paths    cards, folders of cards, or the brief (default: learnings/approved brief.md)
  --trace  print, for each claim, the source line that shares the most with it
Exit code 1 when any claim fails.
"""
import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sourcelib as sl  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = Path(__file__).resolve().parent.parent
FACT_FIELDS = ("title", "Context", "What happened", "What we learned")
BRACKET = re.compile(r"\[([^\]\[]+)\](?!\()")


@dataclass
class Failure:
    file: str
    line: int
    message: str


@dataclass
class Review:
    file: str
    line: int
    terms: list


@dataclass
class Trace:
    file: str
    line: int
    source: str
    source_line: int
    share: float


@dataclass
class Result:
    failures: list = field(default_factory=list)
    reviews: list = field(default_factory=list)
    traces: list = field(default_factory=list)
    claims: int = 0
    items: int = 0

    def add(self, other):
        self.failures += other.failures
        self.reviews += other.reviews
        self.traces += other.traces
        self.claims += other.claims
        self.items += other.items


class Sources:
    """Resolves and loads cited sources once."""

    def __init__(self, root):
        self.root = Path(root)
        self.cache = {}

    def get(self, citation):
        if citation not in self.cache:
            path, why = sl.resolve(citation, self.root)
            self.cache[citation] = (sl.Source(path, self.root), None) if path else (None, why)
        return self.cache[citation]


def check_claim(text, sources, file, line, result):
    """Check one claim against the sources its card or line cites."""
    result.claims += 1
    spans = sl.extract_spans(text)
    seen = set()
    for atom, _, _, shown in spans:
        if atom in seen:
            continue
        seen.add(atom)
        result.items += 1
        if not any(sl.grounded(atom, s) for s in sources):
            kind = {"date": "date", "time": "time", "ver": "version", "id": "identifier",
                    "lit": "term", "qty": "quantity word", "num": "number"}[atom[0]]
            result.failures.append(Failure(file, line, f'{kind} "{shown}" is in no cited source'))
    if sources:
        missing = sorted({w for w in sl.content_words(text) if not any(s.has_word(w) for s in sources)})
        if missing:
            result.reviews.append(Review(file, line, missing))
        best = max(((s,) + sl.best_line(text, s) for s in sources), key=lambda t: t[2])
        result.traces.append(Trace(file, line, best[0].rel, best[1], best[2]))


def load_cited(citations, store, file, line, result):
    sources = []
    for c in citations:
        src, why = store.get(c)
        if src:
            sources.append(src)
        else:
            result.failures.append(Failure(file, line, f'citation "{c}" does not resolve: {why}'))
    return sources


def check_card_text(text, root, file="card", store=None):
    store = store or Sources(root)
    result = Result()
    lines = text.splitlines()
    cites, cite_line, body_start = [], 1, 0
    if lines and lines[0].strip() == "---":
        for i, line in enumerate(lines[1:], 2):
            if line.strip() == "---":
                body_start = i
                break
            if line.startswith("sources:"):
                cite_line = i
                inner = line.split(":", 1)[1].strip().strip("[]")
                cites = [c.strip() for c in inner.split(",") if c.strip()]
    if not cites:
        result.failures.append(Failure(file, cite_line, "the card has no sources"))
    sources = load_cited(cites, store, file, cite_line, result)
    for i, line in enumerate(lines, 1):
        claim = None
        if i <= body_start:
            m = re.match(r"(title|date):\s*(.+)$", line)
            if m:
                claim = m.group(2)
        else:
            m = re.match(r"\*\*([^*]+?):?\*\*:?\s*(.+)$", line.strip())
            claim = m.group(2) if m else (line.strip() or None)
        if claim:
            check_claim(claim, sources, file, i, result)
    return result


def brief_sources(lines):
    """Read the brief's Sources section: short name -> link."""
    names, inside = {}, False
    for line in lines:
        if line.startswith("## "):
            inside = line[3:].strip().lower() == "sources"
            continue
        m = re.match(r"-\s+([^:]+):\s+(.*\S)\s*$", line) if inside else None
        if m:
            names[m.group(1).strip()] = m.group(2).split()[-1]
    return names


def lookup(ref, names):
    """A bracket may add a detail to the short name: [Risks R1], [Channel Sep 09-29]."""
    ref = ref.strip()
    if ref in names:
        return names[ref]
    hits = [n for n in names if ref.startswith(n + " ")]
    return names[max(hits, key=len)] if hits else None


def check_brief_text(text, root, file="brief.md", store=None):
    store = store or Sources(root)
    result = Result()
    lines = sl.strip_header(re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)).splitlines()
    names = brief_sources(lines)
    section = None
    for i, line in enumerate(lines, 1):
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        fact = re.sub(r"^[-*]\s+", "", line.strip())
        if section in (None, "sources") or not fact or fact.lower().rstrip(".") == "none":
            continue
        refs = [r for group in BRACKET.findall(fact) for r in group.split(";")]
        if not refs:
            result.failures.append(Failure(file, i, "fact with no citation"))
            continue
        sources = []
        for ref in refs:
            link = lookup(ref, names)
            if not link:
                result.failures.append(Failure(file, i, f'citation "[{ref.strip()}]" is not in the Sources list'))
                continue
            sources += load_cited([link], store, file, i, result)
        check_claim(BRACKET.sub(" ", fact), sources, file, i, result)
    return result


def check_paths(root, paths):
    root = Path(root)
    store = Sources(root)
    result = Result()
    files = []
    for p in paths:
        p = Path(p)
        files += sorted(p.rglob("*.md")) if p.is_dir() else [p]
    for f in files:
        if not f.is_file():
            continue
        try:
            name = f.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            name = f.as_posix()
        text = f.read_text(encoding="utf-8", errors="replace")
        if f.name == "brief.md":
            result.add(check_brief_text(text, root, name, store))
        else:
            result.add(check_card_text(text, root, name, store))
    return result, len(files)


# ---- mutation test support -------------------------------------------------

def _mutate(atom, shown):
    """Return a wrong version of one item, as text, or None."""
    kind = atom[0]
    if kind == "date":
        m = re.search(r"\d{4}-\d{2}-(\d{2})", shown)
        if m:
            day = int(m.group(1))
            return shown[:m.start(1)] + f"{(day % 27) + 1:02d}" + shown[m.end(1):]
        m = re.search(r"\d{1,2}", shown)
        return shown[:m.start()] + str((int(m.group(0)) % 27) + 1) + shown[m.end():] if m else None
    if kind == "ver":
        return re.sub(r"(\d+)$", lambda m: str(int(m.group(1)) + 5), shown)
    if kind == "num":
        m = re.search(r"\d[\d,]*(?:\.\d+)?", shown)
        if not m:
            return None
        raw = m.group(0).replace(",", "")
        wrong = f"{float(raw) * 2 + 1:g}" if "." in raw else str(int(raw) * 2 + 1)
        return shown[:m.start()] + wrong + shown[m.end():]
    return None


def mutation_run(root, cards):
    """For every number, date and version in each card, write a card with that
    one item made wrong, and check it. Also swap each card's sources for a
    source it does not cite. Return (caught, survived) as lists of labels."""
    root = Path(root)
    store = Sources(root)
    caught, survived = [], []
    all_sources = sorted((root / "sources").glob("*.md"))
    for card in cards:
        text = card.read_text(encoding="utf-8")
        base = {(f.line, f.message) for f in check_card_text(text, root, card.name, store).failures}
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if line.startswith(("id:", "sources:", "supersedes:")):
                continue
            for atom, start, end, shown in sl.extract_spans(line):
                wrong = _mutate(atom, shown)
                if not wrong or wrong == shown or shown not in line:
                    continue
                mutant = "\n".join(lines[:i] + [line.replace(shown, wrong, 1)] + lines[i + 1:])
                after = {(f.line, f.message) for f in check_card_text(mutant, root, card.name, store).failures}
                label = f'{card.name}:{i + 1} "{shown}" -> "{wrong}"'
                (caught if after - base else survived).append(label)
        cited = re.search(r"^sources:\s*\[(.*)\]", text, re.M)
        if cited and sl.extract(text.split("---", 2)[-1]):
            current = {c.strip() for c in cited.group(1).split(",")}
            other = next((f"sources/{s.name}" for s in all_sources if f"sources/{s.name}" not in current), None)
            if other:
                mutant = text.replace(cited.group(0), f"sources: [{other}]", 1)
                after = {(f.line, f.message) for f in check_card_text(mutant, root, card.name, store).failures}
                label = f"{card.name} sources -> [{other}]"
                (caught if after - base else survived).append(label)
    return caught, survived


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("--trace", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--no-review", action="store_true", help="do not print the review terms")
    ap.add_argument("paths", nargs="*")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    paths = [Path(p) if Path(p).is_absolute() else root / p for p in (args.paths or ["learnings/approved", "brief.md"])]
    result, files = check_paths(root, paths)
    for f in result.failures:
        print(f"FAIL   {f.file}:{f.line}: {f.message}")
    if not args.no_review:
        for r in result.reviews:
            print(f"REVIEW {r.file}:{r.line}: not in any cited source: {', '.join(r.terms)}")
    if args.trace:
        for t in result.traces:
            print(f"TRACE  {t.file}:{t.line} -> {t.source}:{t.source_line} (shares {t.share:.0%} of the claim's terms)")
    terms = sum(len(r.terms) for r in result.reviews)
    print(f"{len(result.failures)} failure(s), {terms} review term(s) in {result.claims} claim(s), "
          f"{result.items} checked item(s), {files} file(s)")
    if args.json:
        out = {
            "files": files, "claims": result.claims, "items": result.items,
            "failures": [vars(f) for f in result.failures],
            "reviews": [vars(r) for r in result.reviews],
            "traces": [vars(t) for t in result.traces],
        }
        Path(args.json).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 1 if result.failures else 0


if __name__ == "__main__":
    sys.exit(main())
