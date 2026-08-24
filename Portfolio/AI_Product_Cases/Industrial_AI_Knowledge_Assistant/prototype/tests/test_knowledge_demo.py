import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from knowledge_demo import REGISTERED_EQUIPMENT, load_cases, search_cases, validate_cases


DATASET = ROOT / "data" / "synthetic_failure_cases_v1.jsonl"
SCHEMA = ROOT / "schema" / "failure_case.schema.json"


class SyntheticDatasetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = load_cases(DATASET)

    def test_dataset_contract_is_valid(self):
        self.assertEqual(validate_cases(self.cases), [])

    def test_json_schema_matches_executable_contract(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        from knowledge_demo import REQUIRED_FIELDS

        self.assertEqual(set(schema["required"]), REQUIRED_FIELDS)
        self.assertEqual(set(schema["properties"]["equipment"]["properties"]["id"]["enum"]), REGISTERED_EQUIPMENT)

    def test_case_ids_are_unique(self):
        case_ids = [case["case_id"] for case in self.cases]
        self.assertEqual(len(case_ids), len(set(case_ids)))

    def test_all_records_are_public_safe_synthetic_data(self):
        self.assertTrue(all(case["synthetic"] is True for case in self.cases))
        self.assertTrue(all(case["review"]["status"] == "demo_only" for case in self.cases))

    def test_all_registered_equipment_is_covered(self):
        covered = {case["equipment"]["id"] for case in self.cases}
        self.assertEqual(covered, REGISTERED_EQUIPMENT)

    def test_known_coolant_query_returns_expected_citation(self):
        results = search_cases(self.cases, "coolant pressure low", limit=1)
        self.assertEqual(results[0][1]["case_id"], "SYN-CNC-002")

    def test_known_robot_query_returns_expected_citation(self):
        results = search_cases(self.cases, "robot communication failure", limit=1)
        self.assertEqual(results[0][1]["case_id"], "SYN-ROBOT-002")

    def test_validator_rejects_empty_core_text(self):
        broken = copy.deepcopy(self.cases)
        broken[0]["symptom"] = " "
        self.assertTrue(any("symptom must be a non-empty string" in error for error in validate_cases(broken)))

    def test_validator_rejects_false_review_claim(self):
        broken = copy.deepcopy(self.cases)
        broken[0]["review"]["reviewed_by"] = "unverified expert"
        self.assertTrue(any("reviewed_by must remain null" in error for error in validate_cases(broken)))


if __name__ == "__main__":
    unittest.main()
