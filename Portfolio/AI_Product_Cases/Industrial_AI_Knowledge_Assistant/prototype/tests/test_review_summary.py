import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from summarize_technician_review import summarize_review
from validate_technician_review import FIELDS


class ReviewSummaryTest(unittest.TestCase):
    def write_rows(self, rows):
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", suffix=".csv", delete=False)
        with handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        self.addCleanup(Path(handle.name).unlink)
        return Path(handle.name)

    def complete_rows(self):
        rows = []
        for index in range(1, 11):
            rows.append({field: "" for field in FIELDS})
            rows[-1].update({
                "query_id": f"QP-{index:03d}",
                "query": f"synthetic query {index}",
                "expected_case_id": f"SYN-{index:03d}",
                "plausible_technician_language": "yes",
                "expected_case_correct": "yes",
                "reviewer_role": "maintenance technician",
                "review_date": "2026-10-25",
            })
        return rows

    def test_summary_counts_completed_review(self):
        report = summarize_review(self.write_rows(self.complete_rows()))
        self.assertEqual(report["total_queries"], 10)
        self.assertEqual(report["plausible_language_yes_rate"], 1.0)
        self.assertEqual(report["expected_case_yes_rate"], 1.0)
        self.assertEqual(report["flagged_queries"], [])

    def test_summary_preserves_flags_and_corrections(self):
        rows = self.complete_rows()
        rows[4]["plausible_technician_language"] = "no"
        rows[4]["corrected_query"] = "pressure will not build while demand is high"
        rows[7]["expected_case_correct"] = "uncertain"
        report = summarize_review(self.write_rows(rows))
        self.assertEqual(report["plausible_language_yes_rate"], 0.9)
        self.assertEqual(report["expected_case_yes_rate"], 0.9)
        self.assertEqual([item["query_id"] for item in report["flagged_queries"]], ["QP-005", "QP-008"])

    def test_incomplete_review_is_rejected(self):
        rows = self.complete_rows()
        rows[0]["expected_case_correct"] = ""
        with self.assertRaisesRegex(ValueError, "QP-001"):
            summarize_review(self.write_rows(rows))

    def test_output_excludes_query_text_and_personal_identity_fields(self):
        report = summarize_review(self.write_rows(self.complete_rows()))
        payload = json.dumps(report)
        self.assertNotIn("synthetic query", payload)
        for forbidden in ("reviewer_name", "email", "employer", "site", "customer"):
            self.assertNotIn(f'"{forbidden}"', payload)


if __name__ == "__main__":
    unittest.main()
