#!/usr/bin/env python3
"""Validate the frozen domain-review pack for the five expansion cases."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path


FIELDS = [
    "review_id",
    "case_id",
    "equipment_id",
    "case_fingerprint",
    "technical_plausibility",
    "root_cause_plausibility",
    "troubleshooting_sequence_safe",
    "safety_notes_adequate",
    "correction_required",
    "reviewer_role",
    "review_date",
    "review_notes",
]
NEW_CASE_IDS = [
    "SYN-CNC-003",
    "SYN-ROBOT-003",
    "SYN-COMP-003",
    "SYN-INSPECT-003",
    "SYN-LASER-003",
]
DECISIONS = {"", "yes", "no", "uncertain"}
CORRECTION_DECISIONS = {"", "yes", "no"}
FINGERPRINT_FIELDS = [
    "case_id",
    "equipment",
    "symptom",
    "root_cause",
    "troubleshooting_steps",
    "solution",
    "verification_result",
    "safety_notes",
]


def valid_iso_date(value: str) -> bool:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def load_cases(path: Path) -> dict[str, dict]:
    cases: dict[str, dict] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                case = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"dataset line {line_number}: invalid JSON: {exc.msg}") from exc
            case_id = case.get("case_id")
            if not isinstance(case_id, str):
                raise ValueError(f"dataset line {line_number}: case_id is required")
            cases[case_id] = case
    return cases


def fingerprint_case(case: dict) -> str:
    payload = {field: case[field] for field in FINGERPRINT_FIELDS}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_review(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def validate_review(review_path: Path, dataset_path: Path, require_complete: bool = False) -> list[str]:
    try:
        cases = load_cases(dataset_path)
        header, rows = load_review(review_path)
    except (OSError, ValueError) as exc:
        return [str(exc)]

    errors: list[str] = []
    if header != FIELDS:
        return ["review CSV header does not match the required contract"]

    missing_cases = [case_id for case_id in NEW_CASE_IDS if case_id not in cases]
    if missing_cases:
        errors.append(f"dataset is missing expansion cases: {', '.join(missing_cases)}")
    if len(rows) != len(NEW_CASE_IDS):
        errors.append(f"review row count must be {len(NEW_CASE_IDS)}; found {len(rows)}")

    decision_fields = [
        "technical_plausibility",
        "root_cause_plausibility",
        "troubleshooting_sequence_safe",
        "safety_notes_adequate",
    ]
    for index, (row, case_id) in enumerate(zip(rows, NEW_CASE_IDS), start=1):
        label = row.get("review_id") or f"row {index}"
        case = cases.get(case_id)
        if None in row:
            errors.append(f"{label}: row contains values beyond the required columns")
        if row.get("review_id") != f"NC-{index:03d}":
            errors.append(f"row {index}: review_id must be NC-{index:03d}")
        if row.get("case_id") != case_id:
            errors.append(f"{label}: case_id must remain {case_id}")
        if not case:
            continue
        if row.get("equipment_id") != case["equipment"]["id"]:
            errors.append(f"{label}: equipment_id must match the frozen case")
        if row.get("case_fingerprint") != fingerprint_case(case):
            errors.append(f"{label}: case_fingerprint does not match the frozen case content")

        decisions = {field: row.get(field, "").strip().lower() for field in decision_fields}
        for field, value in decisions.items():
            if value not in DECISIONS:
                errors.append(f"{label}: {field} must be yes, no, uncertain, or blank")
        correction = row.get("correction_required", "").strip().lower()
        if correction not in CORRECTION_DECISIONS:
            errors.append(f"{label}: correction_required must be yes, no, or blank")
        if "no" in decisions.values() and correction != "yes":
            errors.append(f"{label}: correction_required must be yes when any review decision is no")
        if correction == "yes" and not row.get("review_notes", "").strip():
            errors.append(f"{label}: review_notes are required when correction_required is yes")

        annotated = any(decisions.values()) or bool(correction)
        role = row.get("reviewer_role", "").strip()
        review_date = row.get("review_date", "").strip()
        if annotated and not role:
            errors.append(f"{label}: reviewer_role is required for an annotated row")
        if annotated and not valid_iso_date(review_date):
            errors.append(f"{label}: review_date must use YYYY-MM-DD for an annotated row")
        if require_complete and (any(not value for value in decisions.values()) or not correction):
            errors.append(f"{label}: all review decisions are required in complete mode")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review_csv", type=Path)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    errors = validate_review(args.review_csv, args.dataset, args.require_complete)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    mode = "completed review" if args.require_complete else "review template"
    print(f"VALID: {mode} matches the frozen {len(NEW_CASE_IDS)}-case expansion set")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
