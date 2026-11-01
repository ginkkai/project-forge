#!/usr/bin/env python3
"""Summarize a completed technician query review without exposing identity data."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from validate_technician_review import FIELDS, load_review


DECISIONS = {"yes", "no", "uncertain"}


def summarize_review(review_path: Path) -> dict:
    header, rows = load_review(review_path)
    if header != FIELDS:
        raise ValueError("review CSV header does not match the required contract")
    if not rows:
        raise ValueError("review CSV contains no rows")

    incomplete = []
    language_counts: Counter[str] = Counter()
    case_counts: Counter[str] = Counter()
    flagged = []
    roles = set()
    dates = set()

    for row in rows:
        query_id = row["query_id"]
        language = row["plausible_technician_language"].strip().lower()
        case_correct = row["expected_case_correct"].strip().lower()
        if language not in DECISIONS or case_correct not in DECISIONS:
            incomplete.append(query_id)
            continue
        language_counts[language] += 1
        case_counts[case_correct] += 1
        roles.add(row["reviewer_role"].strip())
        dates.add(row["review_date"].strip())
        if language != "yes" or case_correct != "yes":
            flagged.append({
                "query_id": query_id,
                "language_decision": language,
                "case_decision": case_correct,
                "corrected_query": row["corrected_query"].strip() or None,
                "corrected_case_id": row["corrected_case_id"].strip() or None,
                "notes": row["notes"].strip() or None,
            })

    if incomplete:
        raise ValueError("review is incomplete: " + ", ".join(incomplete))

    total = len(rows)
    return {
        "review_contract": "technician_query_review_v1",
        "total_queries": total,
        "plausible_language": dict(sorted(language_counts.items())),
        "expected_case": dict(sorted(case_counts.items())),
        "plausible_language_yes_rate": language_counts["yes"] / total,
        "expected_case_yes_rate": case_counts["yes"] / total,
        "flagged_queries": flagged,
        "reviewer_roles": sorted(role for role in roles if role),
        "review_dates": sorted(value for value in dates if value),
        "privacy_note": "No reviewer names, email addresses, employers, sites, or customer data are included.",
        "interpretation_boundary": "This summarizes query realism and label review only; it is not OEM validation or production-readiness evidence.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review_csv", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = summarize_review(args.review_csv)
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
