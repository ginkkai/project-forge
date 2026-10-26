import unittest
from pathlib import Path


CASE_STUDY = Path(__file__).with_name("PORTFOLIO_CASE_STUDY.md")


class PortfolioCaseStudyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = CASE_STUDY.read_text(encoding="utf-8")

    def test_metrics_match_versioned_evidence(self):
        self.assertIn("10/10 top-1 (100%)", self.text)
        self.assertIn("6/10 top-1 (60%)", self.text)
        self.assertIn("25 unit tests", self.text)

    def test_claim_boundaries_are_explicit(self):
        self.assertIn("Technician review | Not completed", self.text)
        self.assertIn("does not demonstrate production", self.text)
        self.assertIn("not maintenance guidance", self.text)

    def test_reproduction_references_existing_commands(self):
        for name in (
            "knowledge_demo.py",
            "evaluate_retrieval.py",
            "validate_technician_review.py",
            "technician_query_review_v1.csv",
        ):
            self.assertIn(name, self.text)


if __name__ == "__main__":
    unittest.main()
