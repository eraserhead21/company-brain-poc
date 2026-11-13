"""Tests for the contested-value check in scripts/relations_check.py.

Run: python -m unittest discover -s tests -p "test_*.py"

A value that is one side of an open conflict must not stand as a settled
fact in another section of the brief. The first class reproduces the defect
a person found in round 5: the brief lists the backfill cap under Open
conflicts (5k against 4k) and still gives 5k under Decisions.

The fixture in tests/fixtures/contested/ is the round 5 output, unchanged.
"""
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))

import automark  # noqa: E402
import relations_check as rc  # noqa: E402

FIXTURES = REPO / "tests" / "fixtures" / "contested"
R5_BRIEF = (FIXTURES / "r5-brief.md").read_text(encoding="utf-8")
R5_LEDGER = json.loads((FIXTURES / "r5-relations.json").read_text(encoding="utf-8"))

PR7 = "https://github.com/eraserhead21/company-brain-poc/pull/7"
ISSUE12 = "https://github.com/eraserhead21/company-brain-poc/issues/12"
ADR_001 = "decisions/ADR-001-store-readings-in-utc.md"
DESIGN = "sources/alpha-solution-design-v1.md"
WEEKLY_0929 = "sources/alpha-meeting-notes-2026-09-29-weekly.md"
WEEKLY_1013 = "sources/alpha-meeting-notes-2026-10-13-weekly.md"
WEEKLY_1027 = "sources/alpha-meeting-notes-2026-10-27-weekly.md"
STATUS_0930 = "sources/alpha-status-update-2026-09-30.md"
STATUS_1015 = "sources/alpha-status-update-2026-10-15.md"

SOURCES = (
    "## Sources\n\n"
    f"- PR 7: x. {PR7}\n- Issue 12: x. {ISSUE12}\n- ADR-001: x. {ADR_001}\n- Design v1: x. {DESIGN}\n"
    f"- Weekly 09-29: x. {WEEKLY_0929}\n- Weekly 10-13: x. {WEEKLY_1013}\n- Weekly 10-27: x. {WEEKLY_1027}\n"
    f"- Status 09-30: x. {STATUS_0930}\n- Status 10-15: x. {STATUS_1015}\n"
)

CAP = {"id": "backfill-publisher-cap", "topic": "backfill publisher rate cap", "type": "contradiction", "claims": [
    {"value": "Backfill publisher throttled to 5k msg/s", "source": PR7},
    {"value": "Confirmed: the backfill publisher cap is 4k msg/s", "source": WEEKLY_1027}]}
CAP_CONFLICT = ('- Backfill publisher cap: "Backfill publisher throttled to 5k msg/s" [PR 7] vs '
                '"Confirmed: the backfill publisher cap is 4k msg/s" [Weekly 10-27]')
OWNER = {"id": "signoff-owner", "topic": "shadow-run sign-off owner", "type": "contradiction", "claims": [
    {"value": "Shadow-run sign-off owner: PM", "source": STATUS_1015},
    {"value": "The Tech Lead signs off the shadow run before go-live", "source": ISSUE12}]}
OWNER_CONFLICT = ('- Shadow-run sign-off owner: "Shadow-run sign-off owner: PM" [Status 10-15] vs '
                  '"The Tech Lead signs off the shadow run before go-live" [Issue 12]')


def brief(conflicts=(), **sections):
    """A brief with the given lines in each section. Keyword names: decisions,
    status, key_dates, open_risks, supersessions."""
    parts = ["# Project Alpha brief", "", "Compiled: 2026-11-13T00:00:00Z, cursor 2026-11-13T00:00:00Z, by capture", ""]
    for name in ("Status", "Key dates", "Decisions", "Open risks"):
        parts += [f"## {name}", ""] + (list(sections.get(name.lower().replace(" ", "_"), [])) or ["None."]) + [""]
    parts += ["## Open conflicts", ""] + (list(conflicts) or ["None."]) + [""]
    parts += ["## Scope differences", "", "None.", ""]
    parts += ["## Supersessions", ""] + (list(sections.get("supersessions", [])) or ["None."]) + ["", SOURCES]
    return "\n".join(parts)


def contested(relations, brief_text, root=REPO):
    """The messages of the contested-value failures only."""
    result = rc.check({"relations": relations}, root, brief_text)
    return [p.message for p in result.problems if "contested" in p.message]


class Round5Reproduction(unittest.TestCase):
    """The round 5 output, as merged. The check must fail it and name the line."""

    def test_the_check_fails_the_round_5_brief(self):
        msgs = contested(R5_LEDGER["relations"], R5_BRIEF)
        self.assertEqual(len(msgs), 1, msgs)

    def test_the_failure_names_the_line_and_the_section(self):
        msgs = contested(R5_LEDGER["relations"], R5_BRIEF)
        self.assertTrue(any("brief.md:23" in m and "Decisions" in m and "5k msg/s" in m for m in msgs), msgs)

    def test_the_answer_key_rule_fails_the_round_5_brief(self):
        out = automark.Output(FIXTURES)  # the fixture folder holds the brief under another name
        out.set_brief(R5_BRIEF)
        rule = {"auto": {"rule": "not_settled", "all": ["backfill|publisher|cap", "\\b5k\\b|5,000"]}}
        self.assertEqual(automark.mark(rule, out)[0], "fail")


class Fixed(unittest.TestCase):
    """What capture must write instead."""

    def test_a_line_that_says_contested_and_gives_no_value_passes(self):
        b = brief([CAP_CONFLICT], decisions=["- Backfill publisher cap: contested, see Open conflicts [PR 7] [Weekly 10-27]"])
        self.assertEqual(contested([CAP], b), [])

    def test_a_line_with_the_value_and_the_marker_passes(self):
        b = brief([CAP_CONFLICT], decisions=["- Backfill publisher throttled to 5k msg/s (contested, see Open conflicts) [PR 7]"])
        self.assertEqual(contested([CAP], b), [])

    def test_no_line_for_the_item_passes(self):
        b = brief([CAP_CONFLICT], decisions=["- Store all readings in UTC [ADR-001]"])
        self.assertEqual(contested([CAP], b), [])

    def test_the_open_conflicts_section_itself_is_never_a_failure(self):
        self.assertEqual(contested([CAP], brief([CAP_CONFLICT])), [])


class OtherSections(unittest.TestCase):
    def test_the_other_side_under_key_dates_fails(self):
        b = brief([CAP_CONFLICT], key_dates=["- Backfill publisher cap is 4k msg/s [Weekly 10-27]"])
        msgs = contested([CAP], b)
        self.assertTrue(any("Key dates" in m and "4k msg/s" in m for m in msgs), msgs)

    def test_a_contested_value_under_status_fails(self):
        b = brief([CAP_CONFLICT], status=["- Backfill publisher runs at 5k msg/s [PR 7]"])
        self.assertEqual(len(contested([CAP], b)), 1)

    def test_a_supersession_line_that_settles_an_open_conflict_fails(self):
        b = brief([CAP_CONFLICT], supersessions=["- Backfill publisher cap: 5k msg/s [PR 7], now 4k msg/s [Weekly 10-27]"])
        self.assertEqual(len(contested([CAP], b)), 1)


class RedTeam(unittest.TestCase):
    """Cases written to break the check. These held."""

    def test_the_contested_value_cited_from_a_third_source_fails(self):
        # Status 09-30 also gives 5k. A check on the ledger's own source alone would pass this line.
        b = brief([CAP_CONFLICT], decisions=["- Backfill throttle is 5k msg/s [Status 09-30]"])
        self.assertEqual(len(contested([CAP], b)), 1)

    def test_the_same_number_about_another_item_passes(self):
        # 5k msg/s again, for the consumer and from another document.
        b = brief([CAP_CONFLICT], status=["- Load test: Event Hubs throttled above about 5,000 messages per second [Weekly 09-29]"])
        self.assertEqual(contested([CAP], b), [])

    def test_a_conflict_that_a_later_document_resolves_passes(self):
        # The ledger holds a supersession and no contradiction: the new value is settled.
        settled = {"id": "go-live-date", "topic": "go-live date", "type": "supersession", "claims": [
            {"value": "Go-live: 14 November 2026", "source": "sources/alpha-project-charter.md"},
            {"value": "Go-live moved to 28 November 2026 (was 14 November)", "source": STATUS_0930}]}
        b = brief(key_dates=["- Go-live 28 November 2026 [Status 09-30]"])
        self.assertEqual(contested([settled], b), [])

    def test_a_word_value_about_another_item_passes(self):
        # ADR-001 stores readings in UTC. The conflict is about the comparison window.
        window = {"id": "comparison-window", "topic": "shadow-run comparison window", "type": "contradiction", "claims": [
            {"value": "Batch totals use the billing local day (00:00 to 00:00 Amsterdam time)", "source": WEEKLY_1013},
            {"value": "the stream comparison used the UTC day", "source": WEEKLY_1013}]}
        b = brief(['- Comparison window: "Batch totals use the billing local day (00:00 to 00:00 Amsterdam time)" [Weekly 10-13] '
                   'vs "the stream comparison used the UTC day" [Weekly 10-13]'],
                  decisions=["- Store all readings in UTC. Convert to local time only at the billing export [ADR-001]"])
        self.assertEqual(contested([window], b), [])

    def test_a_word_value_stated_as_settled_fails(self):
        b = brief([OWNER_CONFLICT], decisions=["- The PM signs off the shadow run [Status 10-15]"])
        msgs = contested([OWNER], b)
        self.assertTrue(any("Decisions" in m for m in msgs), msgs)

    def test_a_line_that_names_the_item_with_no_value_passes(self):
        b = brief([OWNER_CONFLICT], decisions=["- Shadow run needs a sign-off before go-live [Status 10-15]"])
        self.assertEqual(contested([OWNER], b), [])

    def test_a_value_shared_by_both_sides_is_not_contested(self):
        # Both claims hold "12 partitions". Only the broker differs.
        broker = {"id": "broker", "topic": "message broker", "type": "contradiction", "claims": [
            {"value": "Kafka on AKS, 3 brokers, 12 partitions keyed by meter_id", "source": DESIGN},
            {"value": "Azure Event Hubs (Standard tier, 12 partitions, keyed by meter_id)", "source": "decisions/ADR-002-message-broker.md"}]}
        b = brief(['- Message broker: "Kafka on AKS, 3 brokers, 12 partitions keyed by meter_id" [Design v1] vs '
                   '"Azure Event Hubs (Standard tier, 12 partitions, keyed by meter_id)" [ADR-002]'],
                  status=["- Topic layout: 12 partitions keyed by meter_id [Design v1]"])
        b = b.replace("## Sources\n\n", "## Sources\n\n- ADR-002: x. decisions/ADR-002-message-broker.md\n")
        self.assertEqual(contested([broker], b), [])


class KnownGaps(unittest.TestCase):
    """Pinned gaps. Each passes while the gap is open."""

    def test_a_contested_value_in_a_card_is_not_seen(self):
        # The check reads the brief and the ledger, never the cards. A card
        # that gives 5k as the decision is outside what it tests.
        result = rc.check({"relations": [CAP]}, REPO, brief([CAP_CONFLICT]))
        self.assertEqual([p.message for p in result.problems], [])

    def test_the_same_number_about_another_item_from_the_same_source_fails(self):
        # PR 7 gives 5k twice: the publisher cap, and the point where the broker throttles.
        b = brief([CAP_CONFLICT], open_risks=["- The broker throttles near 5k msg/s [PR 7]"])
        self.assertEqual(len(contested([CAP], b)), 1)

    def test_a_word_value_in_other_words_from_another_source_passes(self):
        # "TL" for "Tech Lead", cited from a document that the ledger does not name.
        b = brief([OWNER_CONFLICT], decisions=["- TL approves the shadow run result [Weekly 10-27]"])
        self.assertEqual(contested([OWNER], b), [])


if __name__ == "__main__":
    unittest.main()
