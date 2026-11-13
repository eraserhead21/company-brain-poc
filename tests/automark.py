"""Mark the judgement tests by script (used by score.py --auto).

Each test in an answer key may carry an "auto" rule. The rule says what the
brief, the cards or the relation ledger must hold for the test to pass.

  conflict      one bullet under "Open conflicts" in the brief matches every
                pattern in "all". An "or" rule, if present, may pass instead.
  supersession  one line outside "Open conflicts" (brief, card or ledger)
                holds the topic, the old value and the new value; the brief
                states the new value; and no open conflict holds both values.
  learning      one card, or the brief, matches every pattern in "all".
  not_conflict  no bullet under "Open conflicts" matches every pattern.
  scope         a scope relation in the ledger, or a bullet under "Scope
                differences", matches every pattern, and no open conflict does.
  not_settled   no brief line outside "Open conflicts" matches every pattern,
                unless the line says "contested".
  ledger_supersession  the ledger holds a supersession from "old" to "new".

Patterns are regular expressions, matched without regard to case. A test with
no rule stays "unmarked" for a person.

This is a keyword check. It is cruder than a person: it can pass a card that
uses the right words for the wrong lesson. tests/test_score_auto.py compares
it with every saved human mark.
"""
import json
import re
from pathlib import Path


class Output:
    """The capture output under one root: brief sections, cards, ledger."""

    def __init__(self, root):
        root = Path(root)
        brief = root / "brief.md"
        self.set_brief(brief.read_text(encoding="utf-8", errors="replace") if brief.is_file() else "")
        self.cards = {}
        for f in sorted((root / "learnings" / "approved").glob("*.md")):
            self.cards[f.name] = f.read_text(encoding="utf-8", errors="replace")
        self.relations = []
        ledger = root / "relations.json"
        if ledger.is_file():
            try:
                self.relations = json.loads(ledger.read_text(encoding="utf-8")).get("relations", [])
            except (ValueError, AttributeError):
                self.relations = []

    def set_brief(self, text):
        self.brief = text
        self.sections = {}
        name = None
        for line in self.brief.splitlines():
            if line.startswith("## "):
                name = line[3:].strip().lower()
                self.sections[name] = []
            elif name and line.strip():
                self.sections[name].append(line.strip())

    def conflicts(self):
        return [l for l in self.sections.get("open conflicts", []) if re.match(r"[-*]\s+", l)]

    def outside_conflicts(self):
        """Brief lines in every section but Open conflicts and Sources."""
        return [l for name, ls in self.sections.items() if name not in ("open conflicts", "sources") for l in ls]

    def lines_outside_conflicts(self):
        """Every line that may record a supersession."""
        lines = [l for name, ls in self.sections.items() if name not in ("open conflicts", "sources") for l in ls]
        if not self.sections:
            lines = self.brief.splitlines()
        for text in self.cards.values():
            lines += text.splitlines()
        for r in self.relations:
            if isinstance(r, dict) and r.get("type") == "supersession":
                values = " ".join(str(c.get("value", "")) for c in r.get("claims", []) if isinstance(c, dict))
                lines.append(f"{r.get('topic', '')} {values}")
        return lines

    def stated(self):
        """Lines where the brief states current facts."""
        if not self.sections:
            return self.brief.splitlines()
        return [l for name, ls in self.sections.items()
                if name not in ("open conflicts", "supersessions", "sources") for l in ls]


def has(pattern, text):
    return re.search(pattern, text, re.I) is not None


def has_all(patterns, text):
    return all(has(p, text) for p in patterns)


def mark(item, out):
    """Return (mark, note) for one test. mark is pass, fail or unmarked."""
    rule = item.get("auto")
    if not rule:
        return "unmarked", "no auto rule"
    kind = rule.get("rule")
    if kind == "conflict":
        for bullet in out.conflicts():
            if has_all(rule["all"], bullet):
                return "pass", f"open conflict: {bullet[:80]}"
        alternatives = rule.get("or") or []
        for other in alternatives if isinstance(alternatives, list) else [alternatives]:
            alt = mark({"auto": other}, out)
            if alt[0] == "pass":
                return "pass", f"alternative: {alt[1]}"
        return "fail", "no bullet under Open conflicts holds both claims"
    if kind == "supersession":
        want = [rule["topic"], rule["old"], rule["new"]]
        if any(has_all([rule["old"], rule["new"]], b) for b in out.conflicts()):
            return "fail", "listed as an open conflict"
        if not any(has_all([rule["topic"], rule["new"]], l) for l in out.stated()):
            return "fail", "the brief does not state the new value"
        for line in out.lines_outside_conflicts():
            if has_all(want, line):
                return "pass", f"recorded: {line.strip()[:80]}"
        return "fail", "no line records the old value and the new one"
    if kind == "learning":
        for name, text in out.cards.items():
            if has_all(rule["all"], text):
                return "pass", f"card {name}"
        if has_all(rule["all"], out.brief):
            return "pass", "brief"
        return "fail", "no card or brief text holds the lesson"
    if kind == "ledger_supersession":
        for r in out.relations:
            if isinstance(r, dict) and r.get("type") == "supersession":
                values = [str(c.get("value", "")) for c in r.get("claims", []) if isinstance(c, dict)]
                if len(values) == 2 and has(rule["old"], values[0]) and has(rule["new"], values[1]):
                    return "pass", f"ledger supersession {r.get('id', '')}"
        return "fail", "no supersession in the ledger"
    if kind == "not_conflict":
        for bullet in out.conflicts():
            if has_all(rule["all"], bullet):
                return "fail", f"listed as an open conflict: {bullet[:80]}"
        return "pass", "not listed as an open conflict"
    if kind == "not_settled":
        for line in out.outside_conflicts():
            if has_all(rule["all"], line) and not has(r"\bcontested\b|\bopen conflicts?\b", line):
                return "fail", f"stated as settled: {line[:80]}"
        return "pass", "no line outside Open conflicts states it as settled"
    if kind == "scope":
        if any(has_all(rule["all"], b) for b in out.conflicts()):
            return "fail", "listed as an open conflict"
        for r in out.relations:
            if isinstance(r, dict) and r.get("type") == "scope":
                text = json.dumps(r)
                if has_all(rule["all"], text):
                    return "pass", f"scope relation {r.get('id', '')}"
        for line in out.sections.get("scope differences", []):
            if has_all(rule["all"], line):
                return "pass", f"scope difference: {line[:80]}"
        return "fail", "not recorded as a scope difference"
    return "unmarked", f"unknown rule {kind}"


def items(key):
    out = []
    for group in ("contradictions", "supersessions", "scopes", "expected_learnings", "negatives", "settled"):
        out += key.get(group, [])
    return out


def mark_all(key, root):
    out = Output(root)
    return {item["id"]: mark(item, out) for item in items(key)}
