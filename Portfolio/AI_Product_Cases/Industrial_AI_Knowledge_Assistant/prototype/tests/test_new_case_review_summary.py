import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from summarize_new_case_review import summarize_review
from validate_new_case_review import FIELDS, load_review


DATASET = ROOT / "data" / "synthetic_failure_cases_v1.jsonl"
REVIEW = ROOT / "data" / "new_case_domain_review_v1.csv"


class NewCaseReviewSummaryTest(unittest.TestCase):
    def write_rows(self, rows):
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", suffix=".csv", delete=False)
        with handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        self.addCleanup(Path(handle.name).unlink)
        return Path(handle.name)

    def complete_rows(self):
        _, rows = load_review(REVIEW)
        for row in rows:
            row.update({
                "technical_plausibility": "yes",
                "root_cause_plausibility": "yes",
                "troubleshooting_sequence_safe": "yes",
                "safety_notes_adequate": "yes",
                "correction_required": "no",
                "reviewer_role": "maintenance technician",
                "review_date": "2026-11-16",
            })
        return rows

    def test_completed_review_is_summarized(self):
        report = summarize_review(self.write_rows(self.complete_rows()), DATASET)
        self.assertEqual(report["total_cases"], 5)
        self.assertEqual(report["yes_rates"]["technical_plausibility"], 1.0)
        self.assertEqual(report["corrections_required"], [])
        self.assertEqual(report["flagged_cases"], [])

    def test_flags_and_corrections_are_preserved(self):
        rows = self.complete_rows()
        rows[2]["safety_notes_adequate"] = "no"
        rows[2]["correction_required"] = "yes"
        rows[2]["review_notes"] = "Add a controlled residual-pressure check."
        report = summarize_review(self.write_rows(rows), DATASET)
        self.assertEqual(report["corrections_required"], ["SYN-COMP-003"])
        self.assertEqual(report["flagged_cases"][0]["case_id"], "SYN-COMP-003")
        self.assertEqual(report["yes_rates"]["safety_notes_adequate"], 0.8)

    def test_incomplete_review_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "review is incomplete or invalid"):
            summarize_review(REVIEW, DATASET)

    def test_fingerprint_drift_is_rejected(self):
        rows = self.complete_rows()
        rows[0]["case_fingerprint"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            summarize_review(self.write_rows(rows), DATASET)

    def test_summary_excludes_free_text_and_personal_identity(self):
        rows = self.complete_rows()
        rows[0]["review_notes"] = "private narrative that must not be copied"
        payload = json.dumps(summarize_review(self.write_rows(rows), DATASET))
        self.assertNotIn("private narrative", payload)
        for forbidden in ("reviewer_name", "reviewer_email", "employer", "customer", "site_name"):
            self.assertNotIn(forbidden, payload)


if __name__ == "__main__":
    unittest.main()
