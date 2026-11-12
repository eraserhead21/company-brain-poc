"""Tests for scripts/provenance_check.py.

Run: python -m unittest discover -s tests -p "test_*.py"

The known-bad cases are the 4 facts that round 1 invented. Their text comes
from git history (see iterations/01-baseline.md), not from memory.
"""
import builtins
import io
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import provenance_check as pc  # noqa: E402

FIX = REPO / "tests" / "fixtures" / "provenance"

CARD = """---
id: 2026-10-01-test-card
title: Test card
type: learning
project: alpha
date: {date}
owner_role: PM
confidence: high
sensitivity: internal
sources: [{sources}]
supersedes: none
---
**Context:** {context}
**What happened:** {happened}
**What we learned:** Plan from a measured test.
"""


def card(happened, sources="sources/alpha-status-update-2026-09-30.md",
         context="The project moved a date.", date="2026-09-30"):
    return CARD.format(happened=happened, sources=sources, context=context, date=date)


def fails(result):
    return [f.message for f in result.failures]


class KnownBadRound1(unittest.TestCase):
    """The 4 round 1 fabrications. 3 must fail. 1 is a reason with no number,
    which this check can only list for review (see the known-gap test)."""

    def test_go_live_delay_of_6_weeks(self):
        r = pc.check_card_text((FIX / "r1-card-go-live-6-weeks.md").read_text(encoding="utf-8"), REPO)
        self.assertTrue(any("6 weeks" in m for m in fails(r)), fails(r))

    def test_same_day_response_time(self):
        r = pc.check_card_text((FIX / "r1-card-same-day-response.md").read_text(encoding="utf-8"), REPO)
        self.assertTrue(any("same-day" in m for m in fails(r)), fails(r))

    def test_backfill_end_date_with_no_source(self):
        r = pc.check_brief_text((FIX / "r1-brief-lines.md").read_text(encoding="utf-8"), REPO)
        self.assertTrue(any("15 Nov" in m for m in fails(r)), fails(r))

    def test_invented_reason_is_listed_for_review(self):
        r = pc.check_brief_text((FIX / "r1-brief-lines.md").read_text(encoding="utf-8"), REPO)
        terms = {t for rv in r.reviews for t in rv.terms}
        self.assertIn("policy", terms)


class Paraphrase(unittest.TestCase):
    """An honest paraphrase must pass. A check that fails these is noise."""

    def test_number_word_and_digit(self):
        r = pc.check_card_text(card("Sandbox access took three weeks on the last project.",
                                    "sources/alpha-meeting-notes-2026-09-15-kickoff.md", date="2026-09-15"), REPO)
        self.assertEqual(fails(r), [])

    def test_date_written_two_ways(self):
        r = pc.check_card_text(card("Go-live moved to 2026-11-28. It was 14 Nov."), REPO)
        self.assertEqual(fails(r), [])

    def test_rate_written_two_ways(self):
        r = pc.check_card_text(card("The broker throttled above 5,000 messages per second, so the cap is 5k msg/s.",
                                    "sources/alpha-meeting-notes-2026-09-29-weekly.md", date="2026-09-29"), REPO)
        self.assertEqual(fails(r), [])


class Fabrication(unittest.TestCase):
    def test_wrong_unit(self):
        r = pc.check_card_text(card("The backfill now needs about 15 weeks."), REPO)
        self.assertTrue(any("15 weeks" in m for m in fails(r)), fails(r))

    def test_fact_from_a_source_the_card_does_not_cite(self):
        # 20 October is in Status 10-01. This card cites only Status 09-30.
        r = pc.check_card_text(card("The customer confirmed the fix for 20 October."), REPO)
        self.assertTrue(any("20 October" in m for m in fails(r)), fails(r))

    def test_invented_version(self):
        r = pc.check_card_text(card("Firmware v2.5 sends malformed timestamps."), REPO)
        self.assertTrue(any("v2.5" in m for m in fails(r)), fails(r))

    def test_brief_fact_with_no_citation(self):
        brief = "# Brief\n\n## Status\n\n- Go-live 28 Nov.\n\n## Sources\n\n- Status 09-30: x. sources/alpha-status-update-2026-09-30.md\n"
        r = pc.check_brief_text(brief, REPO)
        self.assertTrue(any("no citation" in m for m in fails(r)), fails(r))

    def test_brief_citation_not_in_sources_list(self):
        brief = "# Brief\n\n## Status\n\n- Go-live 28 Nov. [Status 11-30]\n\n## Sources\n\n- Status 09-30: x. sources/alpha-status-update-2026-09-30.md\n"
        r = pc.check_brief_text(brief, REPO)
        self.assertTrue(any("Status 11-30" in m for m in fails(r)), fails(r))


class Citations(unittest.TestCase):
    def test_citation_into_tests_folder_fails(self):
        r = pc.check_card_text(card("Go-live moved to 28 November.", "tests/answers/seeds.json"), REPO)
        self.assertTrue(any("outside the source folders" in m for m in fails(r)), fails(r))

    def test_path_that_climbs_out_fails(self):
        r = pc.check_card_text(card("Go-live moved to 28 November.", "sources/../tests/answers/seeds.json"), REPO)
        self.assertTrue(any("leaves the repo" in m or "outside" in m for m in fails(r)), fails(r))

    def test_missing_file_fails(self):
        r = pc.check_card_text(card("Go-live moved to 28 November.", "sources/no-such-file.md"), REPO)
        self.assertTrue(any("not found" in m for m in fails(r)), fails(r))

    def test_issue_in_another_repo_fails(self):
        r = pc.check_card_text(card("Go-live moved to 28 November.", "https://github.com/someone/else/issues/5"), REPO)
        self.assertTrue(any("another repo" in m for m in fails(r)), fails(r))

    def test_card_with_no_sources_fails(self):
        r = pc.check_card_text(card("Go-live moved to 28 November.", ""), REPO)
        self.assertTrue(any("no sources" in m for m in fails(r)), fails(r))

    def test_the_check_never_opens_tests(self):
        opened = []
        real_open, real_read = builtins.open, Path.read_text

        def spy_open(file, *a, **k):
            opened.append(str(file))
            return real_open(file, *a, **k)

        def spy_read(self, *a, **k):
            opened.append(str(self))
            return real_read(self, *a, **k)

        builtins.open, Path.read_text = spy_open, spy_read
        try:
            pc.check_card_text(card("Go-live moved to 28 November.", "tests/answers/seeds.json"), REPO)
            pc.check_paths(REPO, [REPO / "learnings" / "approved", REPO / "brief.md"])
        finally:
            builtins.open, Path.read_text = real_open, real_read
        inside = [p for p in opened if (REPO / "tests") in Path(p).resolve().parents]
        self.assertEqual(inside, [])


class SourceChanges(unittest.TestCase):
    """Red team: a document changes after the card was approved."""

    def test_edited_source_breaks_the_card_that_cites_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(REPO / "sources", root / "sources")
            shutil.copy(REPO / "poc-config.json", root / "poc-config.json")
            text = card("The weekly meeting set raw readings retention at 30 days.",
                        "sources/alpha-meeting-notes-2026-09-29-weekly.md", date="2026-09-29")
            self.assertEqual(fails(pc.check_card_text(text, root)), [])
            doc = root / "sources" / "alpha-meeting-notes-2026-09-29-weekly.md"
            doc.write_text(doc.read_text(encoding="utf-8").replace("30 days", "45 days"), encoding="utf-8")
            r = pc.check_card_text(text, root)
            self.assertTrue(any("30 days" in m for m in fails(r)), fails(r))


class Mutation(unittest.TestCase):
    """Plant one wrong number, date or version in each approved card line and
    count how many the check catches. Survivors are printed, not hidden."""

    def test_mutants(self):
        caught, survived = pc.mutation_run(REPO, sorted((REPO / "learnings" / "approved").glob("*.md")))
        total = len(caught) + len(survived)
        print(f"\nmutation: caught {len(caught)}/{total}")
        for s in survived:
            print(f"  survived: {s}")
        self.assertGreater(total, 30)
        self.assertGreaterEqual(len(caught) / total, 0.9)


class KnownGaps(unittest.TestCase):
    """Pinned gaps. Each test passes while the gap is open. Fix the gap, then
    flip the assertion."""

    def test_negation_is_not_caught(self):
        # The source says "No duplicates seen since." A word check cannot see the reversal.
        r = pc.check_card_text(card("Duplicates were seen after the fix merged last week.",
                                    "sources/alpha-meeting-notes-2026-09-29-weekly.md", date="2026-09-29"), REPO)
        self.assertEqual(fails(r), [])

    def test_wrong_number_that_the_source_also_holds_is_not_caught(self):
        # The source says "about 15 days, not 5". The card swaps them.
        r = pc.check_card_text(card("The full backfill needs 5 days.",
                                    "sources/alpha-meeting-notes-2026-09-29-weekly.md", date="2026-09-29"), REPO)
        self.assertEqual(fails(r), [])

    def test_invented_reason_does_not_fail_the_check(self):
        r = pc.check_brief_text((FIX / "r1-brief-lines.md").read_text(encoding="utf-8"), REPO)
        self.assertFalse(any("policy" in m for m in fails(r)))


if __name__ == "__main__":
    unittest.main()
