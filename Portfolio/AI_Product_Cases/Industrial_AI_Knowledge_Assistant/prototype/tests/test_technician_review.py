import csv
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from validate_technician_review import FIELDS, load_review, validate_review


FIXTURE = ROOT / "data" / "retrieval_eval_paraphrase_v1.jsonl"
REVIEW = ROOT / "data" / "technician_query_review_v1.csv"


class TechnicianReviewTest(unittest.TestCase):
    def write_rows(self, rows):
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", suffix=".csv", delete=False)
        with handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        self.addCleanup(Path(handle.name).unlink)
        return Path(handle.name)

    def test_blank_review_template_is_valid(self):
        self.assertEqual(validate_review(REVIEW, FIXTURE), [])

    def test_complete_mode_rejects_unreviewed_template(self):
        errors = validate_review(REVIEW, FIXTURE, require_complete=True)
        self.assertTrue(any("both review decisions are required" in error for error in errors))

    def test_query_text_cannot_drift_from_frozen_fixture(self):
        _, rows = load_review(REVIEW)
        rows[0]["query"] = "rewritten after seeing retrieval results"
        errors = validate_review(self.write_rows(rows), FIXTURE)
        self.assertTrue(any("query must remain identical" in error for error in errors))

    def test_invalid_decision_is_rejected(self):
        _, rows = load_review(REVIEW)
        rows[0]["plausible_technician_language"] = "maybe"
        errors = validate_review(self.write_rows(rows), FIXTURE)
        self.assertTrue(any("must be yes, no, uncertain, or blank" in error for error in errors))

    def test_annotation_requires_reviewer_role_and_date(self):
        _, rows = load_review(REVIEW)
        rows[0]["plausible_technician_language"] = "yes"
        rows[0]["expected_case_correct"] = "yes"
        errors = validate_review(self.write_rows(rows), FIXTURE)
        self.assertTrue(any("reviewer_role is required" in error for error in errors))
        self.assertTrue(any("review_date must use YYYY-MM-DD" in error for error in errors))

    def test_negative_language_decision_requires_correction(self):
        _, rows = load_review(REVIEW)
        rows[0]["plausible_technician_language"] = "no"
        rows[0]["expected_case_correct"] = "yes"
        rows[0]["reviewer_role"] = "maintenance technician"
        rows[0]["review_date"] = "2026-10-05"
        errors = validate_review(self.write_rows(rows), FIXTURE)
        self.assertTrue(any("corrected_query is required" in error for error in errors))

    def test_completed_review_passes_strict_gate(self):
        _, rows = load_review(REVIEW)
        for row in rows:
            row["plausible_technician_language"] = "yes"
            row["expected_case_correct"] = "yes"
            row["reviewer_role"] = "maintenance technician"
            row["review_date"] = "2026-10-05"
        self.assertEqual(validate_review(self.write_rows(rows), FIXTURE, require_complete=True), [])

    def test_impossible_calendar_date_is_rejected(self):
        _, rows = load_review(REVIEW)
        rows[0]["plausible_technician_language"] = "yes"
        rows[0]["expected_case_correct"] = "yes"
        rows[0]["reviewer_role"] = "maintenance technician"
        rows[0]["review_date"] = "2026-02-31"
        errors = validate_review(self.write_rows(rows), FIXTURE)
        self.assertTrue(any("review_date must use YYYY-MM-DD" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
