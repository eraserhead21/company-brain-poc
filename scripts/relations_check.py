"""Relation check: test every typed relation in relations.json against the sources.

When two sources state different things, capture records one relation:

  contradiction  both claims stand, and a person must decide
  supersession   the later source replaces the earlier claim
  scope          both claims are true, each for a different scope

A supersession needs evidence, and the check finds it in the later source
itself. It does not trust the ledger. The evidence is one of:

  1. a sentence that holds the new value and names the old one after a cue
     ("was 14 November", "not 5", "up from 7");
  2. a sentence that holds the new value and a change word ("moved to",
     "slipped", "now");
  3. a sentence that says it replaces the earlier document by name.

A decision word alone ("agreed", "decided", "confirmed") is not evidence: it
does not show that the team knew the earlier claim. The later source must
also carry a later date than the earlier one.

The check runs both ways. A contradiction whose later source states the
change must be a supersession. There is no model and no network. It never
opens tests/.

A contradiction is open until a person decides. So the check also reads the
brief: a line outside Open conflicts must not give one side of a
contradiction as a fact. The line passes when it says "contested".

What it cannot see: the topic. Two values about different things, joined by
a change word, pass. It also cannot find a relation that capture never wrote.
The contested-value test is a keyword test: it reads the brief, not the
cards, and it can miss a claim with no number that is put in other words.

Usage: python scripts/relations_check.py [--root DIR] [--ledger FILE] [--brief FILE]
Exit code 1 when any relation fails.
"""
import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sourcelib as sl  # noqa: E402
import provenance_check as pc  # noqa: E402  (the brief's citation helpers)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = Path(__file__).resolve().parent.parent
TYPES = ("contradiction", "supersession", "scope")

CHANGE = re.compile(
    r"\b(moved|moves|moving|slipped|slips|now|no longer|instead of|replac(?:es|ed|ing)|supersed(?:es|ed|ing)|"
    r"changed (?:to|from)|postponed|rescheduled|brought forward|pushed (?:back|out|to)|revised to|"
    r"extended to|reduced (?:to|from)|cut (?:to|from)|raised to|lowered to|switched (?:to|from)|"
    r"delayed (?:to|until))\b", re.I)
DECISION = re.compile(r"\b(agreed|decided|confirmed|approved|signed off|chose|chosen|settled|resolved)\b", re.I)
CUE = re.compile(r"\b(?:was|were|not|from|instead of|rather than|previously|formerly|originally)\s+"
                 r"(?:about\s+|around\s+|the\s+)?$", re.I)
REPLACES = re.compile(r"\b(replac\w+|supersed\w+|obsolet\w+|retir\w+)\b", re.I)
CONTESTED = re.compile(r"\bcontested\b|\bopen conflicts?\b", re.I)


@dataclass
class Problem:
    relation: str
    message: str


@dataclass
class Result:
    problems: list = field(default_factory=list)
    evidence: dict = field(default_factory=dict)   # relation id -> (source, line, kind)
    counts: dict = field(default_factory=dict)
    relations: int = 0


def sentences(source):
    """Yield (line number, sentence) for a source."""
    for i, line in enumerate(source.lines, 1):
        for part in re.split(r"(?<=[.!?])\s+", line.strip()):
            if part.strip():
                yield i, part.strip()


def names_old_value(sentence, old_value):
    """True when the sentence gives the old value straight after a cue."""
    wanted = sl.extract(old_value)
    if wanted:
        for atom, start, _, _ in sl.extract_spans(sentence):
            if any(sl.same(w, atom) for w in wanted) and CUE.search(sentence[:start]):
                return True
        return False
    low = sl.normalise(sentence)
    old = re.escape(sl.normalise(old_value))
    return bool(old) and re.search(
        r"\b(?:was|were|not|from|instead of|rather than|previously|formerly|originally)\s+(?:about\s+|around\s+|the\s+)?" + old, low) is not None


def name_words(source):
    """Words that identify a document in running text: 'solution design v1'."""
    stem = Path(source.rel).stem.lower()
    words = [w for w in re.split(r"[-_]", stem) if w and not w.isdigit() and w not in ("alpha", "adr", "issue", "pr")]
    return words


def refers_to(sentence, old):
    low = sentence.lower()
    for kind, label, number in sl.own_ids(old.path):
        if re.search(rf"\b{label}[-\s#]*0*{number}\b", sentence, re.I):
            return True
    words = name_words(old)
    if len(words) < 2 or not all(re.search(rf"\b{re.escape(w)}\b", low) for w in words):
        return False
    return old.date is None or ("date", old.date[1], old.date[2]) in sl.extract(sentence) or not re.search(r"\d{4}-\d{2}-\d{2}", old.rel)


def find_evidence(old_value, old, new_value, new):
    """Look in the later source for proof that it replaces the old claim.
    Return (line, kind) or None."""
    for line, sentence in sentences(new):
        if REPLACES.search(sentence) and old.path != new.path and refers_to(sentence, old):
            return line, "names the document it replaces"
        if not sl.text_has(new_value, sentence):
            continue
        if names_old_value(sentence, old_value):
            return line, "names the old value"
        if CHANGE.search(sentence):
            return line, f'change word "{CHANGE.search(sentence).group(0).lower()}"'
    return None


def decision_note(new_value, new):
    for line, sentence in sentences(new):
        if sl.text_has(new_value, sentence) and DECISION.search(sentence):
            return f' Line {line} has a decision word ("{DECISION.search(sentence).group(0)}"), which is not evidence on its own.'
    return ""


def open_conflicts(brief_text):
    bullets, inside = [], False
    for line in brief_text.splitlines():
        if line.startswith("## "):
            inside = line[3:].strip().lower() == "open conflicts"
            continue
        if inside and re.match(r"\s*[-*]\s+", line):
            bullets.append(re.sub(r"\[[^\]]*\]", " ", re.sub(r"^\s*[-*]\s+", "", line)))
    return bullets


def _short(word):
    """A word cut to a common form, so "throttle" meets "throttled"."""
    s = sl.stem(word)
    return s[:5] if len(s) >= 5 else s


def claim_words(text):
    """The words of a claim that carry meaning: no stop, unit or decision words."""
    out = set()
    for w in sl.WORD.findall(text):
        low = w.lower().strip("'")
        if len(low) >= 2 and low not in sl.STOP and low not in sl.UNITS and not DECISION.fullmatch(low):
            out.add(_short(low))
    return out


@dataclass
class Side:
    """One claim of a contradiction, and what sets it apart from the other claims."""
    value: str
    source: object
    atoms: set          # its own numbers, dates, versions and identifiers
    own_words: set      # its own words, minus the topic
    words: set          # every word of the claim
    has_atoms: bool


def sides_of(topic, loaded):
    atoms = [sl.extract(v) for v, _, _ in loaded]
    words = [claim_words(v) for v, _, _ in loaded]
    topic_words = claim_words(topic)
    sides = []
    for i, (value, src, _) in enumerate(loaded):
        other_atoms = [a for j, group in enumerate(atoms) if j != i for a in group]
        other_words = set().union(*(w for j, w in enumerate(words) if j != i))
        own = {a for a in atoms[i] if not any(sl.same(a, o) or sl.same(o, a) for o in other_atoms)}
        sides.append(Side(value, src, own, words[i] - other_words - topic_words, words[i], bool(atoms[i])))
    numeric = all(s.atoms for s in sides)                       # each side has a number of its own
    item = topic_words | set().union(*words)                    # every word about the item
    common = topic_words | set.intersection(*words)             # the item, without either value
    return sides, numeric, item, common


def states(side, numeric, line, line_words, cites, item, common):
    """True when a brief line gives this side of a conflict as a fact.

    Numbers: the line holds the side's own numbers, and it cites the side's
    source or shares two words with the conflict.
    Words (a conflict where a side has no number of its own): the line cites
    the side's source, holds one of the side's own words and shares two
    words with the item; or the line holds every word of the claim.
    """
    def about(words):
        return bool(words) and len(words & line_words) >= min(2, len(words))

    if side.atoms and all(sl.grounded(a, line) for a in side.atoms) and (cites or about(item)):
        return True
    if numeric:
        return False
    if side.own_words & line_words and cites and about(common):
        return True
    return bool(not side.has_atoms and side.words and side.words <= line_words)


def settled_lines(brief_text):
    """Yield (line number, section, line) for each fact outside Open conflicts and Sources."""
    section = None
    for n, line in enumerate(brief_text.splitlines(), 1):
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        fact = re.sub(r"^[-*]\s+", "", line.strip())
        if section is None or section.lower() in ("open conflicts", "sources"):
            continue
        if fact and fact.lower().rstrip(".") != "none":
            yield n, section, fact


def contested_values(conflicts, brief_text, load, brief_name="brief.md"):
    """A value that is one side of a contradiction must not stand as a fact
    in another section of the brief. Return a Problem for each line that
    gives one, unless the line says that the item is contested."""
    problems = []
    names = pc.brief_sources(brief_text.splitlines())
    parsed = [(rid, sides_of(topic, loaded)) for rid, topic, loaded in conflicts]
    for n, section, fact in settled_lines(brief_text):
        if CONTESTED.search(fact):
            continue
        text = pc.BRACKET.sub(" ", fact)
        line, line_words = sl.Source(text=text), claim_words(text)
        cited = set()
        for group in pc.BRACKET.findall(fact):
            for ref in group.split(";"):
                link = pc.lookup(ref, names)
                src = load(link)[0] if link else None
                if src:
                    cited.add(src.path)
        for rid, (sides, numeric, item, common) in parsed:
            hit = next((s for s in sides if states(s, numeric, line, line_words, s.source.path in cited, item, common)), None)
            if hit:
                problems.append(Problem(rid, (
                    f'{brief_name}:{n} ({section}) states "{hit.value}" as settled, but it is one side of an open '
                    f'conflict: "{fact[:70]}". Take the value out of that line and write '
                    '"<item>: contested, see Open conflicts", with both sources.')))
    return problems


def check(data, root, brief_text=None, brief_name="brief.md"):
    root = Path(root)
    result = Result()
    cache = {}

    def load(citation):
        if citation not in cache:
            path, why = sl.resolve(citation, root)
            cache[citation] = (sl.Source(path, root), None) if path else (None, why)
        return cache[citation]

    relations = data.get("relations") if isinstance(data, dict) else None
    if not isinstance(relations, list):
        result.problems.append(Problem("-", 'the ledger must be an object with a "relations" list'))
        return result
    seen_ids, seen_pairs, conflicts = set(), set(), []
    for n, r in enumerate(relations, 1):
        rid = str(r.get("id") or f"relation {n}") if isinstance(r, dict) else f"relation {n}"
        bad = lambda message, rid=rid: result.problems.append(Problem(rid, message))  # noqa: E731
        result.relations += 1
        if not isinstance(r, dict):
            bad("a relation must be an object")
            continue
        if rid in seen_ids:
            bad("this id is used twice")
        seen_ids.add(rid)
        kind = r.get("type")
        if kind not in TYPES:
            bad(f"type must be one of: {', '.join(TYPES)}")
            continue
        result.counts[kind] = result.counts.get(kind, 0) + 1
        if not str(r.get("topic") or "").strip():
            bad("the relation has no topic")
        claims = r.get("claims")
        if not isinstance(claims, list) or len(claims) < 2 or (kind == "supersession" and len(claims) != 2):
            bad("a supersession needs exactly two claims, old then new; the other types need at least two claims")
            continue
        loaded, ok = [], True
        for c in claims:
            value = str(c.get("value") or "").strip() if isinstance(c, dict) else ""
            cite = str(c.get("source") or "").strip() if isinstance(c, dict) else ""
            if not value or not cite:
                bad("each claim needs a value and a source")
                ok = False
                continue
            src, why = load(cite)
            if not src:
                bad(f'source "{cite}" does not resolve: {why}')
                ok = False
                continue
            if not c.get("redacted") and not sl.text_has(value, src.text):
                bad(f'value "{value}" is not in {src.rel}')
                ok = False
            loaded.append((value, src, c))
        if not ok or len(loaded) < 2:
            continue
        pair = frozenset((sl.normalise(v), s.rel) for v, s, _ in loaded)
        if pair in seen_pairs:
            bad("another relation holds the same two claims")
        seen_pairs.add(pair)
        if len({sl.normalise(v) for v, _, _ in loaded}) < 2 and kind != "scope":
            bad("the claims state the same value")

        if kind == "supersession":
            (old_value, old, _), (new_value, new, _) = loaded
            if old.path != new.path:
                if old.date is None or new.date is None:
                    undated = old.rel if old.date is None else new.rel
                    bad(f"{undated} has no date, so the order of the two sources is not known; record a contradiction")
                    continue
                if new.date <= old.date:
                    bad(f"{new.rel} is not later than {old.rel}; an earlier document cannot replace a later one")
                    continue
            found = find_evidence(old_value, old, new_value, new)
            if found:
                result.evidence[rid] = (new.rel, found[0], found[1])
            else:
                bad(f'no evidence of a change in {new.rel}: no sentence holds "{new_value}" with the old value or a '
                    f"change word, and none names the document it replaces.{decision_note(new_value, new)} "
                    "Record a contradiction.")
        elif kind == "contradiction":
            conflicts.append((rid, str(r.get("topic") or ""), loaded))
            dated = [(v, s) for v, s, _ in loaded if s.date is not None]
            for old_value, old in dated:
                for new_value, new in dated:
                    if new.date > old.date:
                        found = find_evidence(old_value, old, new_value, new)
                        if found:
                            bad(f"{new.rel}:{found[0]} states the change ({found[1]}); the type must be supersession")
        else:
            scopes = [str(c.get("scope") or "").strip() for _, _, c in loaded]
            if not all(scopes):
                bad("each claim in a scope relation must name its scope")
                continue
            if len({sl.normalise(s) for s in scopes}) < 2:
                bad("the claims name the same scope; record a contradiction")
            for scope, (_, src, _) in zip(scopes, loaded):
                if not sl.text_has(scope, src.text):
                    bad(f'scope "{scope}" is not stated in {src.rel}')

    if brief_text is not None:
        bullets = open_conflicts(brief_text)
        matched = set()
        for rid, _, loaded in conflicts:
            hits = [i for i, b in enumerate(bullets) if all(sl.text_has(v, b) for v, _, _ in loaded)]
            if hits:
                matched.update(hits)
            else:
                result.problems.append(Problem(rid, "the brief does not list this contradiction under Open conflicts"))
        for i, b in enumerate(bullets):
            if i not in matched:
                result.problems.append(Problem("brief", f'Open conflicts lists a conflict that is not in the ledger: "{b.strip()[:70]}"'))
        result.problems += contested_values(conflicts, brief_text, load, brief_name)
    return result


def check_text(text, root, brief_text=None, brief_name="brief.md"):
    try:
        data = json.loads(text)
    except ValueError as err:
        result = Result()
        result.problems.append(Problem("-", f"the ledger is not valid JSON: {err}"))
        return result
    return check(data, root, brief_text, brief_name)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("--ledger", default="relations.json")
    ap.add_argument("--brief", default="brief.md")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    ledger = root / args.ledger
    if not ledger.is_file():
        print(f"FAIL   {args.ledger} not found")
        return 1
    brief = root / args.brief
    brief_text = brief.read_text(encoding="utf-8", errors="replace") if brief.is_file() else None
    result = check_text(ledger.read_text(encoding="utf-8", errors="replace"), root, brief_text, args.brief)
    for rid, (src, line, kind) in result.evidence.items():
        print(f"OK     supersession {rid}: {src}:{line} ({kind})")
    for p in result.problems:
        print(f"FAIL   {p.relation}: {p.message}")
    counts = ", ".join(f"{result.counts.get(t, 0)} {t}" for t in TYPES)
    print(f"{len(result.problems)} failure(s) in {result.relations} relation(s): {counts}")
    return 1 if result.problems else 0


if __name__ == "__main__":
    sys.exit(main())
