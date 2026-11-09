import unittest
from pathlib import Path


CASE_STUDY = Path(__file__).resolve().parents[1] / "PORTFOLIO_CASE_STUDY.md"


class PortfolioCaseStudyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = CASE_STUDY.read_text(encoding="utf-8")

    def test_metrics_match_versioned_evidence(self):
        self.assertIn("15/15 top-1 (100%)", self.text)
        self.assertIn("6/10 top-1 (60%)", self.text)
        self.assertIn("42 unit tests", self.text)

    def test_expansion_scope_does_not_overstate_human_review(self):
        self.assertIn("15 cases", self.text)
        self.assertIn("frozen original 10-query review", self.text)
        self.assertIn("must not silently rewrite", self.text)
        self.assertIn("0/5 annotated", self.text)
        self.assertIn("fingerprint binds every review row", self.text)

    def test_claim_boundaries_are_explicit(self):
        self.assertIn("Technician review | Not completed", self.text)
        self.assertIn("does not demonstrate production", self.text)
        self.assertIn("not maintenance guidance", self.text)

    def test_reproduction_references_existing_commands(self):
        for name in (
            "knowledge_demo.py",
            "evaluate_retrieval.py",
            "validate_technician_review.py",
            "validate_new_case_review.py",
            "generate_evidence_report.py",
            "technician_query_review_v1.csv",
            "new_case_domain_review_v1.csv",
        ):
            self.assertIn(name, self.text)


if __name__ == "__main__":
    unittest.main()

