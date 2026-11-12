"""Tests for scripts/relations_check.py.

Run: python -m unittest discover -s tests -p "test_*.py"

The first class reproduces the C1 miss: rounds 2 to 4 recorded "retention
90 days moved to 30 days" as a supersession, on the word "Agreed" alone.
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import relations_check as rc  # noqa: E402

DESIGN = "sources/alpha-solution-design-v1.md"
CHARTER = "sources/alpha-project-charter.md"
WEEKLY_0929 = "sources/alpha-meeting-notes-2026-09-29-weekly.md"
WEEKLY_1013 = "sources/alpha-meeting-notes-2026-10-13-weekly.md"
STATUS_0930 = "sources/alpha-status-update-2026-09-30.md"
STATUS_1001 = "sources/alpha-status-update-2026-10-01.md"
CHANNEL = "sources/alpha-team-channel-log-september.md"
ADR_002 = "decisions/ADR-002-message-broker.md"


def rel(kind, old, new, rid="r1", **extra):
    claims = []
    for c in (old, new):
        claim = {"value": c[0], "source": c[1]}
        if len(c) > 2:
            claim.update(c[2])
        claims.append(claim)
    return {"id": rid, "topic": "test", "type": kind, "claims": claims, **extra}


def problems(relation, root=REPO, brief=None):
    return [p.message for p in rc.check({"relations": [relation]}, root, brief).problems]


class C1Reproduction(unittest.TestCase):
    """What main records today: a supersession with no evidence of a change."""

    def test_agreed_alone_is_not_a_supersession(self):
        msgs = problems(rel("supersession", ("90 days", DESIGN), ("30 days", WEEKLY_0929)))
        self.assertTrue(any("no evidence of a change" in m for m in msgs), msgs)

    def test_the_same_pair_passes_as_a_contradiction(self):
        self.assertEqual(problems(rel("contradiction", ("90 days", DESIGN), ("30 days", WEEKLY_0929))), [])

    def test_was_in_the_next_sentence_is_not_evidence(self):
        # "Storage cost was the reason." has "was", but not about the old value.
        result = rc.check({"relations": [rel("supersession", ("90 days", DESIGN), ("30 days", WEEKLY_0929))]}, REPO)
        self.assertEqual(result.evidence, {})


class RealSupersessions(unittest.TestCase):
    """The supersessions that rounds 2 to 4 got right must still pass."""

    def test_moved_to_with_the_old_value(self):
        self.assertEqual(problems(rel("supersession", ("14 November 2026", CHARTER), ("28 November 2026", STATUS_0930))), [])

    def test_slipped(self):
        self.assertEqual(problems(rel("supersession", ("20 October", STATUS_1001), ("27 October", WEEKLY_1013))), [])

    def test_now_with_not_the_old_value(self):
        self.assertEqual(problems(rel("supersession", ("5 days", DESIGN), ("15 days", WEEKLY_0929))), [])

    def test_old_and_new_value_in_one_document(self):
        self.assertEqual(problems(rel("supersession", ("17 November", WEEKLY_1013), ("19 November", WEEKLY_1013))), [])

    def test_a_real_supersession_typed_as_a_conflict_fails(self):
        msgs = problems(rel("contradiction", ("14 November 2026", CHARTER), ("28 November 2026", STATUS_0930)))
        self.assertTrue(any("states the change" in m for m in msgs), msgs)


class Order(unittest.TestCase):
    def test_older_document_cannot_supersede_a_newer_one(self):
        msgs = problems(rel("supersession", ("28 November 2026", STATUS_0930), ("14 November 2026", CHARTER)))
        self.assertTrue(any("is not later than" in m for m in msgs), msgs)

    def test_document_with_no_date_cannot_supersede(self):
        msgs = problems(rel("supersession", ("meter local time", DESIGN), ("UTC", CHANNEL)))
        self.assertTrue(any("has no date" in m for m in msgs), msgs)


class Grounding(unittest.TestCase):
    def test_value_that_is_not_in_its_source_fails(self):
        msgs = problems(rel("contradiction", ("60 days", DESIGN), ("30 days", WEEKLY_0929)))
        self.assertTrue(any('"60 days" is not in' in m for m in msgs), msgs)

    def test_source_in_tests_folder_fails(self):
        msgs = problems(rel("contradiction", ("90 days", "tests/answers/seeds.json"), ("30 days", WEEKLY_0929)))
        self.assertTrue(any("outside the source folders" in m for m in msgs), msgs)

    def test_redacted_value_is_not_checked_against_the_source(self):
        r = rel("contradiction", ("Engineer A", CHANNEL, {"redacted": True}), ("Engineer B", STATUS_0930, {"redacted": True}))
        self.assertEqual(problems(r), [])

    def test_change_word_about_another_value_is_not_evidence(self):
        # Weekly 10-13 has "moved to 19 November" and, in the next sentence, "Go-live stays 28 November".
        msgs = problems(rel("supersession", ("14 November 2026", CHARTER), ("28 November", WEEKLY_1013)))
        self.assertTrue(any("no evidence of a change" in m for m in msgs), msgs)

    def test_old_value_named_without_a_change_cue_is_not_evidence(self):
        # ADR-002 names Kafka ("Kafka-protocol clients still work"), but states no change from it.
        msgs = problems(rel("supersession", ("Kafka", DESIGN), ("Event Hubs", ADR_002)))
        self.assertTrue(any("no evidence of a change" in m for m in msgs), msgs)


class Shape(unittest.TestCase):
    def test_unknown_type_fails(self):
        msgs = problems(rel("update", ("90 days", DESIGN), ("30 days", WEEKLY_0929)))
        self.assertTrue(any("type must be" in m for m in msgs), msgs)

    def test_one_claim_fails(self):
        r = {"id": "x", "topic": "t", "type": "contradiction", "claims": [{"value": "90 days", "source": DESIGN}]}
        self.assertTrue(any("two claims" in m for m in problems(r)))

    def test_text_that_is_not_json_fails_and_does_not_crash(self):
        result = rc.check_text("{ not json", REPO)
        self.assertTrue(any("not valid JSON" in p.message for p in result.problems))

    def test_same_pair_typed_twice_fails(self):
        data = {"relations": [
            rel("contradiction", ("90 days", DESIGN), ("30 days", WEEKLY_0929), rid="a"),
            rel("contradiction", ("90 days", DESIGN), ("30 days", WEEKLY_0929), rid="b"),
        ]}
        msgs = [p.message for p in rc.check(data, REPO).problems]
        self.assertTrue(any("same two claims" in m for m in msgs), msgs)


class Scope(unittest.TestCase):
    def test_scope_difference_with_both_scopes_in_the_sources(self):
        r = rel("scope", ("2,000 messages per second", ADR_002, {"scope": "peak in steady state"}),
                ("5,000 messages per second", WEEKLY_0929, {"scope": "backfill"}))
        self.assertEqual(problems(r), [])

    def test_scope_that_the_source_does_not_state_fails(self):
        r = rel("scope", ("2,000 messages per second", ADR_002, {"scope": "weekend traffic"}),
                ("5,000 messages per second", WEEKLY_0929, {"scope": "backfill"}))
        self.assertTrue(any("scope" in m for m in problems(r)))

    def test_scope_with_no_scope_named_fails(self):
        r = rel("scope", ("2,000 messages per second", ADR_002), ("5,000 messages per second", WEEKLY_0929))
        self.assertTrue(any("scope" in m for m in problems(r)))


class NewDocuments(unittest.TestCase):
    """Documents that the rules were not written against, in a temp copy."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        shutil.copytree(REPO / "sources", self.root / "sources")
        shutil.copytree(REPO / "decisions", self.root / "decisions")
        shutil.copy(REPO / "poc-config.json", self.root / "poc-config.json")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel_path, text):
        (self.root / rel_path).write_text(text, encoding="utf-8")
        return rel_path

    def test_decision_word_with_the_old_value_is_a_supersession(self):
        doc = self.write("sources/notes-2026-11-02.md", "NOTES\n\n2 November 2026.\n\n- Agreed: the shadow run is 10 days, up from 7.\n")
        self.assertEqual(problems(rel("supersession", ("7-day", CHARTER), ("10 days", doc)), self.root), [])

    def test_decision_word_alone_in_a_new_document_is_not(self):
        doc = self.write("sources/notes-2026-11-02.md", "NOTES\n\n2 November 2026.\n\n- Decided: the shadow run is 10 days.\n")
        msgs = problems(rel("supersession", ("7-day", CHARTER), ("10 days", doc)), self.root)
        self.assertTrue(any("no evidence of a change" in m for m in msgs), msgs)

    def test_record_that_names_the_document_it_replaces(self):
        adr = self.write("decisions/ADR-009-broker-in-design.md",
                         "# ADR-009\n\n- Date: 2026-11-02\n\n## Decision\n\nAzure Event Hubs is the broker.\n"
                         "This record replaces section 2 of Solution Design v1.\n")
        self.assertEqual(problems(rel("supersession", ("Kafka on AKS", DESIGN), ("Azure Event Hubs", adr)), self.root), [])

    def test_document_dated_before_the_other_cannot_supersede_it(self):
        doc = self.write("sources/review-2026-09-12.md", "REVIEW\n\n12 September 2026.\n\n- Partition count moved to 24.\n")
        msgs = problems(rel("supersession", ("12 partitions", ADR_002), ("24", doc)), self.root)
        self.assertTrue(any("is not later than" in m for m in msgs), msgs)


class BriefAgreement(unittest.TestCase):
    BRIEF = ("# Brief\n\n## Open conflicts\n\n"
             "- Raw readings retention. 90 days. [Design v1] Versus 30 days. [Weekly 09-29]\n\n"
             "## Sources\n\n- Design v1: x. " + DESIGN + "\n- Weekly 09-29: x. " + WEEKLY_0929 + "\n")

    def test_conflict_in_ledger_and_brief(self):
        r = rel("contradiction", ("90 days", DESIGN), ("30 days", WEEKLY_0929))
        self.assertEqual(problems(r, brief=self.BRIEF), [])

    def test_conflict_in_ledger_but_not_in_brief(self):
        r = rel("contradiction", ("Kafka on AKS", DESIGN), ("Azure Event Hubs", ADR_002))
        msgs = [p.message for p in rc.check({"relations": [r]}, REPO, self.BRIEF).problems]
        self.assertTrue(any("under Open conflicts" in m for m in msgs), msgs)
        self.assertTrue(any("not in the ledger" in m for m in msgs), msgs)


class KnownGaps(unittest.TestCase):
    """Pinned gaps. Each passes while the gap is open."""

    def test_the_check_does_not_know_the_topic(self):
        # Backfill-complete date against the shadow-run date: two topics, one change word.
        r = rel("supersession", ("17 October 2026", CHARTER), ("17 November", STATUS_0930))
        self.assertEqual(problems(r), [])


if __name__ == "__main__":
    unittest.main()
