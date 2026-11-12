"""Red-team cases for scripts/redaction_check.py, the pattern backstop.

Run: python -m unittest discover -s tests -p "test_*.py"

The backstop is the second layer, behind the redaction rules that the model
follows. These cases write a confidential detail in a form the patterns were
not built for: in words, as a paraphrase, with no keyword, split in two.
"Caught" cases must stay caught. "KnownGaps" cases pass while the backstop
misses them: the model is then the only layer.
"""
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import redaction_check  # noqa: E402


def hits(text):
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "card.md"
        f.write_text(text + "\n", encoding="utf-8")
        return [name for _, _, name, _ in redaction_check.scan(f)]


class Caught(unittest.TestCase):
    def test_phone_in_local_format(self):
        self.assertIn("phone", hits("The engineer's new mobile is 06-1111 2222."))

    def test_date_of_birth_in_words(self):
        self.assertIn("dob", hits("The contractor was born on 7 June 1988."))

    def test_date_of_birth_in_iso_form(self):
        self.assertIn("dob", hits("HR needs the DOB (1988-06-07) for the site pass."))

    def test_pay_with_a_currency_sign(self):
        self.assertIn("money", hits("The day rate is €900."))

    def test_iso_date_alone_is_not_a_phone_number(self):
        self.assertEqual(hits("Go-live is 2026-11-28."), [])


class KnownGaps(unittest.TestCase):
    """The pattern backstop misses each of these today."""

    def test_pay_written_in_words(self):
        self.assertEqual(hits("The day rate goes up to nine hundred euros from December."), [])

    def test_health_with_no_keyword(self):
        self.assertEqual(hits("One engineer is recovering from an operation and works half days."), [])

    def test_token_with_no_colon_after_the_keyword(self):
        self.assertEqual(hits("His token for the perf rig is ghp_test_51ab77c0de93."), [])

    def test_vendor_switch_as_a_paraphrase(self):
        self.assertEqual(hits("The customer may walk away to another supplier."), [])

    def test_customer_account_with_no_prefix(self):
        self.assertEqual(hits("Their account with us is 7741 2209."), [])

    def test_name_split_into_initial_and_surname(self):
        # The backstop holds no names. Only the model, and the answer key in score.py, check names.
        self.assertEqual(hits("D. Kovac will send the load-test scripts."), [])


if __name__ == "__main__":
    unittest.main()
