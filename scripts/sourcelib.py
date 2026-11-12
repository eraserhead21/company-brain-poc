"""Shared source handling for the provenance and relation checks.

Two jobs:
  1. Turn a citation (a repo path, a GitHub issue or PR URL, an old Drive URL)
     into a file under the source folders, or say why it does not resolve.
  2. Pull the checkable items out of a piece of text: numbers with their
     unit, dates, times, versions, identifiers and quantity words.

It reads only sources/, decisions/, docs/ and src/. It never opens tests/, so
capture can run these checks without seeing an answer key.
"""
import json
import re
from pathlib import Path

SOURCE_ROOTS = ("sources", "decisions", "docs", "src")

MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}
MONTH_RE = (r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|"
            r"Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)")

NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
                "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}

# Units of time and rate. A number with one of these must keep its unit.
UNITS = {
    "s": "s", "sec": "s", "secs": "s", "second": "s", "seconds": "s",
    "min": "min", "mins": "min", "minute": "min", "minutes": "min",
    "h": "h", "hr": "h", "hrs": "h", "hour": "h", "hours": "h",
    "day": "day", "days": "day", "week": "week", "weeks": "week",
    "month": "month", "months": "month", "year": "year", "years": "year",
    "msg": "msg", "msgs": "msg", "message": "msg", "messages": "msg",
}

STOP = set("""a an the of at to and or for in on per by with from is are was were be been it its
this that than then not no as about above under over into near after before since until we our
their they will would can could must may now also so if but while which who what when where
how why all any each every both more most less least very just only out up down off
because some them through against well does took have has had make made makes take takes
being there these those other others such same still even once again ever never here
versus acting wrong neither says said source sources january february march april june july
august september october november december""".split())

# Words that redaction puts in place of a name. They are never in a source.
ROLE_WORDS = set("""pm tl engineer engineers team tech lead customer customers contact project
manager role owner""".split())

# Quantity words. Left: how a claim says it. Right: how a source may say it.
QUANTITY = {
    "same-day": (r"\bsame[- ]day\b", [r"\bsame[- ]day\b"]),
    "overnight": (r"\bovernight\b", [r"\bovernight\b"]),
    "hourly": (r"\bhourly\b", [r"\bhourly\b", r"\b(?:per|an|each|every) hour\b"]),
    "daily": (r"\bdaily\b", [r"\bdaily\b", r"\b(?:per|a|each|every) day\b"]),
    "weekly": (r"\bweekly\b", [r"\bweekly\b", r"\b(?:per|a|each|every) week\b"]),
    "monthly": (r"\bmonthly\b", [r"\bmonthly\b", r"\b(?:per|a|each|every) month\b"]),
    "twice": (r"\btwice\b", [r"\btwice\b", r"\btwo times\b", r"\b2x\b"]),
    "double": (r"\bdoubl(?:e|ed|es|ing)\b", [r"\bdoubl\w+", r"\btwice\b", r"\b2x\b"]),
    "half": (r"\bhal(?:f|ved|ves|ving)\b", [r"\bhal(?:f|ved|ves|ving)\b"]),
    "triple": (r"\btripl(?:e|ed|es|ing)\b", [r"\btripl\w+", r"\b3x\b", r"\bthree times\b"]),
}

GH_URL = re.compile(r"^https://github\.com/([^/\s]+/[^/\s]+)/(issues|pull)/(\d+)/?$")
DRIVE_URL = re.compile(r"^https://docs\.google\.com/document/d/([\w-]+)")
HEADER = re.compile(r"\A\s*<!--.*?-->", re.S)
WORD = re.compile(r"[A-Za-z][A-Za-z']*")


def stem(word):
    w = word.lower().strip("'")
    if w.endswith("'s"):
        w = w[:-2]
    for suffix in ("ing", "ed", "es", "s"):
        if w.endswith(suffix) and len(w) - len(suffix) >= 3:
            return w[: -len(suffix)]
    return w


def config(root):
    path = Path(root) / "poc-config.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def repo_names(root):
    cfg = config(root)
    names = [cfg.get("repo", "")] + list(cfg.get("repo_aliases", []))
    return {n.lower() for n in names if n}


def strip_header(text):
    """Blank the export comment at the top, and keep the line numbers.
    The comment holds the export date, which is not a fact of the document."""
    m = HEADER.match(text)
    if not m:
        return text
    return "\n" * text[: m.end()].count("\n") + text[m.end():]


def _drive_index(root):
    index = {}
    folder = Path(root) / "sources"
    if folder.is_dir():
        for f in sorted(folder.glob("*.md")):
            head = f.read_text(encoding="utf-8", errors="replace")[:600]
            m = re.search(r"Drive file ([\w-]+)", head)
            if m:
                index[m.group(1)] = f"sources/{f.name}"
    return index


def resolve(citation, root):
    """Return (path, None) for a citation that points at a source file, or
    (None, reason). A path outside the source folders is refused before any
    file is opened."""
    root = Path(root)
    cite = citation.strip().strip("<>")
    if not cite:
        return None, "empty citation"
    m = GH_URL.match(cite)
    d = DRIVE_URL.match(cite)
    if m:
        names = repo_names(root)
        if names and m.group(1).lower() not in names:
            return None, "the URL is for another repo"
        rel = f"sources/github/{'issue' if m.group(2) == 'issues' else 'pr'}-{m.group(3)}.md"
    elif d:
        rel = _drive_index(root).get(d.group(1))
        if not rel:
            return None, "no export in sources/ for this Drive document"
    elif re.match(r"^[a-z][a-z0-9+.-]*://", cite, re.I):
        return None, "the URL is not a known source"
    else:
        rel = cite
    parts = Path(rel.replace("\\", "/")).parts
    if Path(rel).is_absolute() or ".." in parts:
        return None, "the path leaves the repo"
    if not parts or parts[0] not in SOURCE_ROOTS:
        return None, "the path is outside the source folders"
    full = root.joinpath(*parts)
    if not full.is_file():
        if m:
            return None, f"snapshot not found ({rel}); run scripts/snapshot_github.py"
        return None, "file not found"
    if root.resolve() not in full.resolve().parents:
        return None, "the path leaves the repo"
    return full, None


def own_ids(path):
    """Identifiers a source carries in its own file name, such as ADR-002."""
    ids = set()
    name = Path(path).name.lower()
    for label, pattern in (("ADR", r"adr-(\d+)"), ("ISSUE", r"issue-(\d+)"), ("PR", r"pr-(\d+)")):
        for n in re.findall(pattern, name):
            ids.add(("id", label, int(n)))
    return ids


class Source:
    def __init__(self, path=None, root=None, text=None):
        """A source file, or (with text=) a piece of text treated like one."""
        if text is None:
            self.path = Path(path)
            self.rel = self.path.relative_to(root).as_posix()
            self.text = strip_header(self.path.read_text(encoding="utf-8", errors="replace"))
            ids = own_ids(self.path)
        else:
            self.path, self.rel, self.text, ids = None, "", text, set()
        self.lines = self.text.splitlines()
        self.atoms = extract(self.text) | ids
        self.low = normalise(self.text)
        self.stems = {stem(w) for w in WORD.findall(self.text)}
        self.prefixes = {w.lower()[:5] for w in WORD.findall(self.text) if len(w) >= 4}
        self.date = doc_date(self.lines)

    def has_quantity(self, name):
        return any(re.search(p, self.text, re.I) for p in QUANTITY[name][1])

    def has_word(self, word):
        w = word.lower()
        return stem(w) in self.stems or (len(w) >= 4 and w[:5] in self.prefixes)


def normalise(text):
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip().lower()


def doc_date(lines):
    """The document's own date: the first full date near its top. None when
    the document does not state one."""
    seen = 0
    for line in lines:
        if not line.strip():
            continue
        seen += 1
        if seen > 8:
            break
        m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", line)
        if m and 1 <= int(m.group(2)) <= 12:
            return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        m = re.search(rf"\b(\d{{1,2}})\s+({MONTH_RE})\s+(\d{{4}})\b", line)
        if m:
            return (int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1)))
    return None


def _blank(text, start, end):
    return text[:start] + " " * (end - start) + text[end:]


def _neighbours(text, start, end):
    """The unit after a number, and the words around it."""
    # Stay inside the sentence: the next sentence says nothing about this number.
    after = re.split(r"[.;:!?()\n]", text[end:end + 60])[0]
    before = re.split(r"[.;:!?()\n]", text[max(0, start - 40):start])[-1]
    unit = None
    nxt = re.match(r"[\s-]*([A-Za-z][A-Za-z/]*)", after)
    if nxt:
        first = nxt.group(1).split("/")[0].lower()
        unit = UNITS.get(first)
    ctx = set()
    words_after = [w.split("/")[0].lower() for w in re.findall(r"[A-Za-z][A-Za-z/]*", after)][:3]
    for w in [w for w in words_after if w not in STOP][:2]:
        ctx.add(UNITS.get(w, stem(w)))
    words_before = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z/]*", before)]
    if words_before and words_before[-1] not in STOP:
        ctx.add(UNITS.get(words_before[-1], stem(words_before[-1])))
    return unit, frozenset(ctx)


def extract_spans(text):
    """Return [(atom, start, end, shown)] for every checkable item in text.

    Atoms:
      ("date", month, day)        28 Nov, 28 November 2026, 2026-11-28
      ("time", "02:00")
      ("ver", "2.3")              v2.3
      ("id", "ADR", 1)            ADR-001, PR 7, Issue 12, R1
      ("lit", "2026-13-01")       a token that must appear as written
      ("qty", "daily")            a quantity word
      ("num", value, unit, ctx)   a number, its unit, and the words around it
    """
    found = []
    work = text

    def take(pattern, build, flags=0):
        nonlocal work
        for m in list(re.finditer(pattern, work, flags)):
            for atom in build(m):
                found.append((atom, m.start(), m.end(), m.group(0).strip()))
            work = _blank(work, m.start(), m.end())

    def iso(m):
        month, day = int(m.group(2)), int(m.group(3))
        if 1 <= month <= 12 and 1 <= day <= 31:
            return [("date", month, day)]
        return [("lit", m.group(1) + "-" + m.group(2) + "-" + m.group(3))]

    take(r"\b(\d{4})-(\d{2})-(\d{2})(?:T[\d:]+)?\b", iso)
    take(rf"\b((?:\d{{1,2}}(?:st|nd|rd|th)?\s*(?:to|and|or|,|-)\s*)*\d{{1,2}}(?:st|nd|rd|th)?)\s+({MONTH_RE})\b(?:\s+\d{{4}})?",
         lambda m: [("date", MONTHS[m.group(2).lower()], int(d)) for d in re.findall(r"\d+", m.group(1))], re.I)
    take(rf"\b({MONTH_RE})\s+(\d{{1,2}})(?:st|nd|rd|th)?\b(?![:\d])(?:,?\s+\d{{4}})?",
         lambda m: [("date", MONTHS[m.group(1).lower()], int(m.group(2)))], re.I)
    take(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", lambda m: [("lit", m.group(0))])
    take(r"\b(\d{1,2}):(\d{2})\b", lambda m: [("time", f"{int(m.group(1)):02d}:{m.group(2)}")])
    take(r"\bv(\d+(?:\.\d+)*)\b", lambda m: [("ver", m.group(1))], re.I)
    take(r"\b(ADR|PR|CR|Issue)[-\s#]*(\d+)\b", lambda m: [("id", m.group(1).upper(), int(m.group(2)))], re.I)
    take(r"\bR(\d{1,2})\b", lambda m: [("id", "R", int(m.group(1)))])
    take(r"\b[a-z]+(?:_[a-z]+)+\b", lambda m: [("lit", m.group(0))])
    for name, (claim_pattern, _) in QUANTITY.items():
        take(claim_pattern, lambda m, name=name: [("qty", name)], re.I)

    def word_number(m):
        unit = UNITS.get(m.group(2).lower())
        return [("num", float(NUMBER_WORDS[m.group(1).lower()]), unit, frozenset({unit}))] if unit else []

    for m in list(re.finditer(r"\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)[\s-]+([A-Za-z]+)\b", work, re.I)):
        atoms = word_number(m)
        if atoms:
            found.append((atoms[0], m.start(), m.end(), m.group(0).strip()))
            work = _blank(work, m.start(), m.end())

    number = re.compile(r"(?<![\w.,/-])(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(\s?%|[kK]\b|M\b|x\b)?(?![A-Za-z\d])")
    for m in number.finditer(work):
        value = float(m.group(1).replace(",", "") + (m.group(2) or ""))
        suffix = (m.group(3) or "").strip()
        unit, ctx = _neighbours(work, m.start(), m.end())
        if not suffix and not unit and not m.group(2) and 1900 <= value <= 2100 and "," not in m.group(1):
            continue  # a year on its own
        if suffix in ("k", "K"):
            value *= 1_000
        elif suffix == "M":
            value *= 1_000_000
        elif suffix == "%":
            unit = "pct"
        elif suffix == "x":
            unit = "x"
        shown = m.group(0).strip()
        tail = re.match(r"[\s-]*([A-Za-z][A-Za-z/]*)", work[m.end():m.end() + 30])
        if unit and unit not in ("pct", "x") and tail:
            shown = work[m.start():m.end() + tail.end()].strip()
        found.append((("num", value, unit, ctx), m.start(), m.end(), shown))
    return found


def extract(text):
    return {atom for atom, _, _, _ in extract_spans(text)}


def grounded(atom, source):
    """True when the source holds this item."""
    kind = atom[0]
    if kind == "lit":
        return atom[1].lower() in source.low
    if kind == "qty":
        return source.has_quantity(atom[1])
    if kind != "num":
        return atom in source.atoms
    return any(same_number(atom, other) for other in source.atoms)


def same_number(atom, other):
    """True when two number items say the same thing."""
    if atom[0] != "num" or other[0] != "num" or atom[1] != other[1]:
        return False
    _, _, unit, ctx = atom
    _, _, o_unit, o_ctx = other
    if unit:
        # Same value and same unit, or a bare number on the other side ("not 5").
        return o_unit == unit or (o_unit is None and not o_ctx)
    return bool(not ctx or not o_ctx or ctx & o_ctx or (o_unit and o_unit in ctx))


def same(atom, other):
    return same_number(atom, other) if atom[0] == "num" else atom == other


def text_has(value, text):
    """True when the text holds the value: every item in it, or, for a value
    with no number or date, every word of it."""
    atoms = extract(value)
    if atoms:
        return all(grounded(a, Source(text=text)) for a in atoms)
    words = [w for w in re.findall(r"[A-Za-z0-9_]+", value.lower()) if w not in STOP]
    have = {stem(w) for w in re.findall(r"[A-Za-z0-9_]+", text.lower())}
    return bool(words) and all(stem(w) in have for w in words)


def content_words(text):
    """Words long enough to carry meaning, minus stop words and role words."""
    out = []
    for w in WORD.findall(text):
        low = w.lower().strip("'")
        if len(low) >= 5 and low not in STOP and low not in ROLE_WORDS and stem(low) not in ROLE_WORDS:
            out.append(low)
    return out


def best_line(text, source):
    """The source line that shares the most with the text: (line number, share).
    A pointer for a person to follow. It is not proof."""
    want = {stem(w) for w in content_words(text)} | {a for a in extract(text) if a[0] != "num"}
    best, best_score = 0, 0.0
    if not want:
        return best, best_score
    for i, line in enumerate(source.lines, 1):
        if not line.strip():
            continue
        have = {stem(w) for w in content_words(line)} | {a for a in extract(line) if a[0] != "num"}
        score = len(want & have) / len(want)
        if score > best_score:
            best, best_score = i, score
    return best, round(best_score, 2)
