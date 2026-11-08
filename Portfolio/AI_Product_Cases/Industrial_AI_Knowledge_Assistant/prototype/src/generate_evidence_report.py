#!/usr/bin/env python3
"""Generate one privacy-safe JSON snapshot of the prototype evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from evaluate_retrieval import evaluate, load_evaluations
from knowledge_demo import REGISTERED_EQUIPMENT, load_cases, validate_cases
from validate_technician_review import load_review, validate_review


def _metric(report: dict) -> dict:
    return {
        "passed": report["passed"],
        "total": report["total"],
        "top_1_accuracy": report["accuracy"],
    }


def build_evidence_report(root: Path) -> dict:
    data = root / "data"
    dataset = data / "synthetic_failure_cases_v1.jsonl"
    exact_fixture = data / "retrieval_eval_v1.jsonl"
    paraphrase_fixture = data / "retrieval_eval_paraphrase_v1.jsonl"
    review_csv = data / "technician_query_review_v1.csv"

    cases = load_cases(dataset)
    errors = validate_cases(cases)
    if errors:
        raise ValueError("dataset validation failed: " + "; ".join(errors))

    exact = evaluate(cases, load_evaluations(exact_fixture))
    paraphrase = evaluate(cases, load_evaluations(paraphrase_fixture))
    _, review_rows = load_review(review_csv)
    annotated_rows = sum(
        bool(row["plausible_technician_language"].strip() or row["expected_case_correct"].strip())
        for row in review_rows
    )
    review_complete = not validate_review(review_csv, paraphrase_fixture, require_complete=True)

    return {
        "artifact_version": "synthetic-industrial-dataset-v1",
        "dataset": {
            "case_count": len(cases),
            "equipment_ids_covered": len({case["equipment"]["id"] for case in cases}),
            "registered_equipment_ids": len(REGISTERED_EQUIPMENT),
            "synthetic_only": all(case["synthetic"] is True for case in cases),
        },
        "retrieval": {
            "exact_term": _metric(exact),
            "paraphrase_stress": _metric(paraphrase),
        },
        "coverage_scope": {
            "dataset_cases": len(cases),
            "exact_term_fixture_cases": exact["total"],
            "frozen_domain_review_fixture_cases": len(review_rows),
            "domain_review_scope": "original_10_case_subset",
        },
        "domain_review": {
            "status": "completed" if review_complete else "not_completed",
            "annotated_rows": annotated_rows,
            "total_rows": len(review_rows),
            "claim_boundary": "No technician, OEM, or field validation claim is permitted until the complete review gate passes.",
        },
        "safety_boundary": "Synthetic prototype evidence only; not maintenance guidance or production-accuracy evidence.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="prototype directory (default: parent of src)",
    )
    parser.add_argument("--output", type=Path, help="optional JSON output path")
    args = parser.parse_args()

    try:
        report = build_evidence_report(args.root)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1

    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
