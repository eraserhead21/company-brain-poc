"""Tests for the auto marker (tests/automark.py, used by score.py --auto).

Run: python -m unittest discover -s tests -p "test_*.py"

The agreement test replays every saved round: it takes the cards and the
brief from the commit that round scored, marks them with the script, and
compares the result with the marks a person saved in tests/results/.
"""
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tests"))

import automark  # noqa: E402

# Saved round -> (commit whose output the round scored, answer key).
ROUNDS = {
    "r1-2026-10-01": ("741e4e7", "seeds.json"),
    "r2-2026-11-03": ("7ef0ddd", "seeds.json"),
    "r3-2026-11-03": ("ce4878f", "seeds.json"),
    "r4-holdout-2026-11-03": ("8b3a8a4", "holdout.json"),
    "r4-regression-2026-11-03": ("8b3a8a4", "seeds.json"),
    "r5-holdout-2026-11-12": ("f5331fb", "holdout5.json"),
}

# Where the script and the person disagree. The person is right in each case.
# The script took a card and a Key dates line as the record of a replaced fact.
KNOWN_MISMATCHES = ["r5-holdout-2026-11-12 H5S1"]


def key(name):
    return json.loads((REPO / "tests" / "answers" / name).read_text(encoding="utf-8"))


def checkout(commit, into):
    done = subprocess.run(["git", "-C", str(REPO), "archive", commit, "learnings", "brief.md"], capture_output=True)
    if done.returncode != 0:
        return False
    with tarfile.open(fileobj=io.BytesIO(done.stdout)) as tar:
        tar.extractall(into, filter="data")
    return True


def agreement():
    """Return (matched, total, mismatches) over every saved round."""
    matched, total, mismatches = 0, 0, []
    for run, (commit, key_name) in ROUNDS.items():
        saved = json.loads((REPO / "tests" / "results" / f"{run}.json").read_text(encoding="utf-8"))
        human = {i["id"]: i["mark"] for i in saved["hand_checks"]["items"]}
        with tempfile.TemporaryDirectory() as tmp:
            if not checkout(commit, tmp):
                return None
            auto = automark.mark_all(key(key_name), Path(tmp))
        for item, mark in human.items():
            total += 1
            got = auto[item][0]
            if got == mark:
                matched += 1
            else:
                mismatches.append(f"{run} {item}: person {mark}, script {got} ({auto[item][1]})")
    return matched, total, mismatches


def root_with(brief="", cards=None, ledger=None):
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / "learnings" / "approved").mkdir(parents=True)
    (root / "brief.md").write_text(brief, encoding="utf-8")
    for name, text in (cards or {}).items():
        (root / "learnings" / "approved" / name).write_text(text, encoding="utf-8")
    if ledger is not None:
        (root / "relations.json").write_text(json.dumps(ledger), encoding="utf-8")
    return tmp, root


CONFLICT = {"id": "C1", "auto": {"rule": "conflict", "all": ["retention", r"\b90\b", r"\b30\b"]}}
SUPERSESSION = {"id": "S1", "auto": {"rule": "supersession", "topic": "go-live", "old": "14 Nov", "new": "28 Nov"}}


class Agreement(unittest.TestCase):
    def test_script_agrees_with_every_saved_human_mark(self):
        got = agreement()
        if got is None:
            self.skipTest("the round commits are not in this clone (shallow checkout)")
        matched, total, mismatches = got
        print(f"\nauto marker agreement with saved human marks: {matched}/{total}")
        for m in mismatches:
            print(f"  mismatch: {m}")
        self.assertEqual(total, 62)
        self.assertEqual([m.split(":")[0] for m in mismatches], KNOWN_MISMATCHES)


class Rules(unittest.TestCase):
    def mark(self, item, **files):
        tmp, root = root_with(**files)
        try:
            return automark.mark(item, automark.Output(root))[0]
        finally:
            tmp.cleanup()

    def test_conflict_under_open_conflicts_passes(self):
        brief = "## Open conflicts\n\n- Raw readings retention. 90 days. [A] Versus 30 days. [B]\n"
        self.assertEqual(self.mark(CONFLICT, brief=brief), "pass")

    def test_same_values_under_supersessions_fail_the_conflict_test(self):
        brief = "## Open conflicts\n\nNone.\n\n## Supersessions\n\n- Raw readings retention 90 days moved to 30 days. [A] to [B]\n"
        self.assertEqual(self.mark(CONFLICT, brief=brief), "fail")

    def test_supersession_needs_the_new_value_in_the_brief(self):
        brief = "## Status\n\n- Go-live 14 Nov. [A]\n\n## Supersessions\n\n- Go-live 14 Nov moved to 28 Nov. [A] to [B]\n"
        self.assertEqual(self.mark(SUPERSESSION, brief=brief), "fail")

    def test_supersession_listed_as_open_conflict_fails(self):
        brief = "## Status\n\n- Go-live 28 Nov. [B]\n\n## Open conflicts\n\n- Go-live. 14 Nov. [A] Versus 28 Nov. [B]\n"
        self.assertEqual(self.mark(SUPERSESSION, brief=brief), "fail")

    def test_item_with_no_rule_is_left_for_a_person(self):
        self.assertEqual(self.mark({"id": "X1"}, brief=""), "unmarked")


class RedTeam(unittest.TestCase):
    """Attempts to pass a test without doing the work."""

    def mark(self, item, **files):
        tmp, root = root_with(**files)
        try:
            return automark.mark(item, automark.Output(root))[0]
        finally:
            tmp.cleanup()

    def test_conflict_words_scattered_over_two_bullets_do_not_pass(self):
        brief = "## Open conflicts\n\n- Raw readings retention. [A]\n- Broker. 90 days versus 30 days. [B]\n"
        self.assertEqual(self.mark(CONFLICT, brief=brief), "fail")

    def test_conflict_named_only_in_a_card_does_not_pass(self):
        card = "---\nid: x\n---\n**What happened:** Retention 90 days versus 30 days is an open conflict.\n"
        self.assertEqual(self.mark(CONFLICT, brief="## Open conflicts\n\nNone.\n", cards={"x.md": card}), "fail")

    def test_ledger_alone_does_not_pass_a_conflict_the_brief_hides(self):
        ledger = {"relations": [{"id": "r", "topic": "Raw readings retention", "type": "contradiction",
                                 "claims": [{"value": "90 days", "source": "a"}, {"value": "30 days", "source": "b"}]}]}
        self.assertEqual(self.mark(CONFLICT, brief="## Open conflicts\n\nNone.\n", ledger=ledger), "fail")

    def test_listing_everything_as_a_conflict_fails_the_trap(self):
        trap = {"id": "HN1", "auto": {"rule": "not_conflict", "all": ["dry.?run"]}}
        brief = "## Open conflicts\n\n- Dry run start. Monday. [A] Versus 12 October. [B]\n"
        self.assertEqual(self.mark(trap, brief=brief), "fail")


if __name__ == "__main__":
    unittest.main()
