#!/usr/bin/env python3
"""Summarize a completed five-case domain review without copying free text."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from validate_new_case_review import load_review, validate_review


DECISION_FIELDS = [
    "technical_plausibility",
    "root_cause_plausibility",
    "troubleshooting_sequence_safe",
    "safety_notes_adequate",
]


def summarize_review(review_path: Path, dataset_path: Path) -> dict:
    errors = validate_review(review_path, dataset_path, require_complete=True)
    if errors:
        raise ValueError("review is incomplete or invalid: " + "; ".join(errors))

    _, rows = load_review(review_path)
    counts = {field: Counter() for field in DECISION_FIELDS}
    flagged_cases = []
    corrections_required = []
    roles = set()
    dates = set()

    for row in rows:
        decisions = {field: row[field].strip().lower() for field in DECISION_FIELDS}
        for field, value in decisions.items():
            counts[field][value] += 1
        correction = row["correction_required"].strip().lower()
        if correction == "yes":
            corrections_required.append(row["case_id"])
        if correction == "yes" or any(value != "yes" for value in decisions.values()):
            flagged_cases.append({
                "review_id": row["review_id"],
                "case_id": row["case_id"],
                "decisions": decisions,
                "correction_required": correction,
            })
        roles.add(row["reviewer_role"].strip())
        dates.add(row["review_date"].strip())

    total = len(rows)
    return {
        "review_contract": "new_case_domain_review_v1",
        "total_cases": total,
        "decision_counts": {
            field: dict(sorted(field_counts.items()))
            for field, field_counts in counts.items()
        },
        "yes_rates": {
            field: field_counts["yes"] / total
            for field, field_counts in counts.items()
        },
        "corrections_required": corrections_required,
        "flagged_cases": flagged_cases,
        "reviewer_roles": sorted(role for role in roles if role),
        "review_dates": sorted(value for value in dates if value),
        "free_text_excluded": True,
        "privacy_note": "Free-text notes and reviewer identity fields are excluded from this summary.",
        "interpretation_boundary": "This is domain-review evidence for five synthetic cases only; it is not OEM validation, maintenance guidance, or production-readiness evidence.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review_csv", type=Path)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = summarize_review(args.review_csv, args.dataset)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
