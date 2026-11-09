import csv
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from validate_new_case_review import FIELDS, load_review, validate_review


DATASET = ROOT / "data" / "synthetic_failure_cases_v1.jsonl"
REVIEW = ROOT / "data" / "new_case_domain_review_v1.csv"


class NewCaseReviewTest(unittest.TestCase):
    def write_rows(self, rows):
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", suffix=".csv", delete=False)
        with handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        self.addCleanup(Path(handle.name).unlink)
        return Path(handle.name)

    def test_blank_review_pack_is_valid(self):
        self.assertEqual(validate_review(REVIEW, DATASET), [])

    def test_complete_mode_rejects_blank_pack(self):
        errors = validate_review(REVIEW, DATASET, require_complete=True)
        self.assertTrue(any("all review decisions are required" in error for error in errors))

    def test_case_fingerprint_prevents_content_drift(self):
        _, rows = load_review(REVIEW)
        rows[0]["case_fingerprint"] = "0" * 64
        errors = validate_review(self.write_rows(rows), DATASET)
        self.assertTrue(any("fingerprint does not match" in error for error in errors))

    def test_annotation_requires_role_and_date(self):
        _, rows = load_review(REVIEW)
        rows[0]["technical_plausibility"] = "yes"
        errors = validate_review(self.write_rows(rows), DATASET)
        self.assertTrue(any("reviewer_role is required" in error for error in errors))
        self.assertTrue(any("review_date must use YYYY-MM-DD" in error for error in errors))

    def test_negative_decision_requires_correction_and_notes(self):
        _, rows = load_review(REVIEW)
        rows[0].update({
            "technical_plausibility": "no",
            "root_cause_plausibility": "yes",
            "troubleshooting_sequence_safe": "yes",
            "safety_notes_adequate": "yes",
            "correction_required": "no",
            "reviewer_role": "maintenance technician",
            "review_date": "2026-11-09",
        })
        errors = validate_review(self.write_rows(rows), DATASET)
        self.assertTrue(any("correction_required must be yes" in error for error in errors))

        rows[0]["correction_required"] = "yes"
        errors = validate_review(self.write_rows(rows), DATASET)
        self.assertTrue(any("review_notes are required" in error for error in errors))

    def test_completed_review_passes_strict_gate(self):
        _, rows = load_review(REVIEW)
        for row in rows:
            row.update({
                "technical_plausibility": "yes",
                "root_cause_plausibility": "yes",
                "troubleshooting_sequence_safe": "yes",
                "safety_notes_adequate": "yes",
                "correction_required": "no",
                "reviewer_role": "maintenance technician",
                "review_date": "2026-11-09",
            })
        self.assertEqual(validate_review(self.write_rows(rows), DATASET, require_complete=True), [])

    def test_contract_contains_no_personal_identity_fields(self):
        forbidden = {"name", "email", "employer", "customer", "site"}
        self.assertFalse(forbidden.intersection(FIELDS))


if __name__ == "__main__":
    unittest.main()
