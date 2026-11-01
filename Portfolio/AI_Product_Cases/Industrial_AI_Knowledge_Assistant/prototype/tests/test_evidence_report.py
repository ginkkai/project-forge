import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from generate_evidence_report import build_evidence_report, main


class EvidenceReportTest(unittest.TestCase):
    def test_report_reproduces_published_evidence(self):
        report = build_evidence_report(ROOT)
        self.assertEqual(report["dataset"]["case_count"], 10)
        self.assertEqual(report["dataset"]["equipment_ids_covered"], 5)
        self.assertEqual(report["retrieval"]["exact_term"]["top_1_accuracy"], 1.0)
        self.assertEqual(report["retrieval"]["paraphrase_stress"]["top_1_accuracy"], 0.6)

    def test_blank_review_is_not_reported_as_domain_evidence(self):
        report = build_evidence_report(ROOT)
        self.assertEqual(report["domain_review"]["status"], "not_completed")
        self.assertEqual(report["domain_review"]["annotated_rows"], 0)
        self.assertIn("No technician", report["domain_review"]["claim_boundary"])

    def test_report_is_privacy_safe_and_machine_readable(self):
        report = build_evidence_report(ROOT)
        rendered = json.dumps(report)
        for forbidden in ("reviewer_name", "reviewer_email", "employer", "customer", "site_name"):
            self.assertNotIn(forbidden, rendered)


if __name__ == "__main__":
    unittest.main()
