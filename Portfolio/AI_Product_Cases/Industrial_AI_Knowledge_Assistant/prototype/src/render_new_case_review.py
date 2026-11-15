#!/usr/bin/env python3
"""Render a reviewer-facing Markdown worksheet for the five expansion cases."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from validate_new_case_review import NEW_CASE_IDS, load_cases, load_review


DECISION_LABELS = [
    ("technical_plausibility", "Technical plausibility"),
    ("root_cause_plausibility", "Root-cause plausibility"),
    ("troubleshooting_sequence_safe", "Troubleshooting sequence safe"),
    ("safety_notes_adequate", "Safety notes adequate"),
    ("correction_required", "Correction required"),
]


def display(value: str) -> str:
    value = value.strip()
    return value if value else "Not reviewed"


def render_worksheet(dataset_path: Path, review_path: Path) -> str:
    cases = load_cases(dataset_path)
    header, rows = load_review(review_path)
    if len(rows) != len(NEW_CASE_IDS):
        raise ValueError(f"review row count must be {len(NEW_CASE_IDS)}; found {len(rows)}")

    lines = [
        "# Five-Case Expansion Review Worksheet",
        "",
        "This worksheet is generated from the versioned synthetic dataset and review CSV.",
        "It is a reviewer aid, not evidence of a completed review. Record decisions in",
        "`data/new_case_domain_review_v1.csv`, then run the strict validator.",
        "",
        "Allowed values are `yes`, `no`, or `uncertain`; `correction_required` accepts",
        "`yes` or `no`. Do not enter names, email addresses, employers, customers, sites,",
        "real incident details, credentials, or proprietary information.",
        "",
    ]

    for index, (case_id, row) in enumerate(zip(NEW_CASE_IDS, rows), start=1):
        case = cases[case_id]
        lines.extend([
            f"## {index}. {case_id} — {case['equipment']['type']}",
            "",
            f"- **Review ID:** `{row['review_id']}`",
            f"- **Equipment ID:** `{case['equipment']['id']}`",
            f"- **Case fingerprint:** `{row['case_fingerprint']}`",
            f"- **Synthetic error code:** `{case['error_code']}`",
            "",
            f"**Symptom:** {case['symptom']}",
            "",
            f"**Proposed root cause:** {case['root_cause']}",
            "",
            "**Troubleshooting steps:**",
            "",
        ])
        lines.extend(f"{step_index}. {step}" for step_index, step in enumerate(case["troubleshooting_steps"], start=1))
        lines.extend([
            "",
            f"**Proposed solution:** {case['solution']}",
            "",
            f"**Verification result:** {case['verification_result']}",
            "",
            "**Safety notes:**",
            "",
        ])
        lines.extend(f"- {note}" for note in case["safety_notes"])
        lines.extend(["", "**Review decisions:**", ""])
        lines.extend(f"- {label}: **{display(row[field])}**" for field, label in DECISION_LABELS)
        lines.extend([
            f"- Reviewer role: **{display(row['reviewer_role'])}**",
            f"- Review date: **{display(row['review_date'])}**",
            f"- Review notes: **{display(row['review_notes'])}**",
            "",
        ])

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("review_csv", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path, help="fail if this committed worksheet differs")
    args = parser.parse_args()

    try:
        rendered = render_worksheet(args.dataset, args.review_csv)
        if args.check:
            if args.check.read_text(encoding="utf-8") != rendered:
                print(f"ERROR: {args.check} is stale; regenerate it from the dataset and review CSV", file=sys.stderr)
                return 1
            print(f"VALID: {args.check} matches the versioned dataset and review CSV")
            return 0
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
    except (KeyError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
