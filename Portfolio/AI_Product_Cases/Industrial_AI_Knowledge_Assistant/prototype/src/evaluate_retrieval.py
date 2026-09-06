#!/usr/bin/env python3
"""Evaluate deterministic retrieval against a versioned synthetic query set."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from knowledge_demo import load_cases, search_cases, validate_cases


def load_evaluations(path: Path) -> list[dict]:
    evaluations: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {line_number}: invalid JSON: {exc.msg}") from exc
            if set(item) != {"query", "expected_case_id", "category"}:
                raise ValueError(f"line {line_number}: evaluation fields must be query, expected_case_id, category")
            if not all(isinstance(item[field], str) and item[field].strip() for field in item):
                raise ValueError(f"line {line_number}: evaluation fields must be non-empty strings")
            evaluations.append(item)
    if not evaluations:
        raise ValueError("evaluation set contains no queries")
    return evaluations


def evaluate(cases: list[dict], evaluations: list[dict]) -> dict:
    case_ids = {case["case_id"] for case in cases}
    rows: list[dict] = []
    for item in evaluations:
        expected = item["expected_case_id"]
        if expected not in case_ids:
            raise ValueError(f"expected case is missing from dataset: {expected}")
        matches = search_cases(cases, item["query"], limit=1)
        actual = matches[0][1]["case_id"] if matches else None
        rows.append({**item, "actual_case_id": actual, "passed": actual == expected})

    passed = sum(row["passed"] for row in rows)
    return {
        "metric": "top_1_accuracy",
        "passed": passed,
        "total": len(rows),
        "accuracy": passed / len(rows),
        "results": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("evaluation_set", type=Path)
    parser.add_argument("--json", action="store_true", help="print machine-readable results")
    args = parser.parse_args()

    try:
        cases = load_cases(args.dataset)
        errors = validate_cases(cases)
        if errors:
            raise ValueError("dataset validation failed: " + "; ".join(errors))
        report = evaluate(cases, load_evaluations(args.evaluation_set))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for row in report["results"]:
            status = "PASS" if row["passed"] else "FAIL"
            print(f"{status} | {row['query']} | expected={row['expected_case_id']} | actual={row['actual_case_id']}")
        print(f"TOP-1 ACCURACY: {report['passed']}/{report['total']} ({report['accuracy']:.0%})")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
