import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from render_new_case_review import render_worksheet
from validate_new_case_review import NEW_CASE_IDS


DATASET = ROOT / "data" / "synthetic_failure_cases_v1.jsonl"
REVIEW = ROOT / "data" / "new_case_domain_review_v1.csv"
WORKSHEET = ROOT / "NEW_CASE_REVIEW_WORKSHEET.md"


class NewCaseReviewWorksheetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rendered = render_worksheet(DATASET, REVIEW)
        cls.committed = WORKSHEET.read_text(encoding="utf-8")

    def test_committed_worksheet_is_current(self):
        self.assertEqual(self.committed, self.rendered)

    def test_all_five_expansion_cases_are_visible(self):
        for case_id in NEW_CASE_IDS:
            self.assertEqual(self.committed.count(f"## {NEW_CASE_IDS.index(case_id) + 1}. {case_id}"), 1)

    def test_reviewer_sees_case_content_and_decisions(self):
        for label in (
            "Symptom",
            "Proposed root cause",
            "Troubleshooting steps",
            "Safety notes",
            "Technical plausibility",
            "Correction required",
        ):
            self.assertIn(label, self.committed)

    def test_blank_state_is_explicit(self):
        self.assertEqual(self.committed.count("Technical plausibility: **Not reviewed**"), 5)
        self.assertIn("not evidence of a completed review", self.committed)

    def test_worksheet_has_no_personal_identity_fields(self):
        for forbidden in ("Reviewer name", "Reviewer email", "Employer", "Customer name", "Site name"):
            self.assertNotIn(forbidden, self.committed)


if __name__ == "__main__":
    unittest.main()
