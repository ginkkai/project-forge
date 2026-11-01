#!/usr/bin/env python3
"""Validate technician review annotations against the frozen paraphrase fixture."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path


FIELDS = [
    "query_id",
    "query",
    "expected_case_id",
    "plausible_technician_language",
    "expected_case_correct",
    "corrected_query",
    "corrected_case_id",
    "reviewer_role",
    "review_date",
    "notes",
]
DECISIONS = {"", "yes", "no", "uncertain"}


def valid_iso_date(value: str) -> bool:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def load_fixture(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"fixture line {line_number}: invalid JSON: {exc.msg}") from exc
            if not isinstance(item.get("query"), str) or not isinstance(item.get("expected_case_id"), str):
                raise ValueError(f"fixture line {line_number}: query and expected_case_id are required")
            rows.append(item)
    if not rows:
        raise ValueError("fixture contains no queries")
    return rows


def load_review(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        return header, list(reader)


def validate_review(review_path: Path, fixture_path: Path, require_complete: bool = False) -> list[str]:
    try:
        fixture = load_fixture(fixture_path)
        header, rows = load_review(review_path)
    except (OSError, ValueError) as exc:
        return [str(exc)]

    errors: list[str] = []
    if header != FIELDS:
        errors.append("review CSV header does not match the required contract")
        return errors
    if len(rows) != len(fixture):
        errors.append(f"review row count must match fixture: expected {len(fixture)}, found {len(rows)}")

    known_case_ids = {item["expected_case_id"] for item in fixture}
    expected_ids = [f"QP-{index:03d}" for index in range(1, len(fixture) + 1)]
    seen_ids: set[str] = set()

    for index, (row, source) in enumerate(zip(rows, fixture), start=1):
        label = row.get("query_id") or f"row {index}"
        if None in row:
            errors.append(f"{label}: row contains values beyond the required columns")
        if row.get("query_id") != expected_ids[index - 1]:
            errors.append(f"row {index}: query_id must be {expected_ids[index - 1]}")
        if label in seen_ids:
            errors.append(f"{label}: duplicate query_id")
        seen_ids.add(label)
        if row.get("query") != source["query"]:
            errors.append(f"{label}: query must remain identical to the frozen fixture")
        if row.get("expected_case_id") != source["expected_case_id"]:
            errors.append(f"{label}: expected_case_id must remain identical to the frozen fixture")

        language = row.get("plausible_technician_language", "").strip().lower()
        case_correct = row.get("expected_case_correct", "").strip().lower()
        if language not in DECISIONS:
            errors.append(f"{label}: plausible_technician_language must be yes, no, uncertain, or blank")
        if case_correct not in DECISIONS:
            errors.append(f"{label}: expected_case_correct must be yes, no, uncertain, or blank")
        if language == "no" and not row.get("corrected_query", "").strip():
            errors.append(f"{label}: corrected_query is required when technician language is marked no")
        corrected_case = row.get("corrected_case_id", "").strip()
        if case_correct == "no" and corrected_case not in known_case_ids:
            errors.append(f"{label}: corrected_case_id must name a case from the fixture when expected case is marked no")

        reviewed = language != "" or case_correct != ""
        role = row.get("reviewer_role", "").strip()
        date = row.get("review_date", "").strip()
        if reviewed and not role:
            errors.append(f"{label}: reviewer_role is required for an annotated row")
        if reviewed and not valid_iso_date(date):
            errors.append(f"{label}: review_date must use YYYY-MM-DD for an annotated row")
        if require_complete and (language == "" or case_correct == ""):
            errors.append(f"{label}: both review decisions are required in complete mode")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review_csv", type=Path)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    errors = validate_review(args.review_csv, args.fixture, args.require_complete)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    mode = "completed review" if args.require_complete else "review template"
    print(f"VALID: {mode} matches the frozen {len(load_fixture(args.fixture))}-query fixture")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
