#!/usr/bin/env python3
"""Validate and search the public-safe Project Forge synthetic dataset."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_FIELDS = {
    "case_id",
    "synthetic",
    "equipment",
    "error_code",
    "symptom",
    "root_cause",
    "troubleshooting_steps",
    "solution",
    "verification_result",
    "safety_notes",
    "source",
    "review",
    "tags",
}
REGISTERED_EQUIPMENT = {"CNC-001", "ROBOT-001", "COMP-001", "INSPECT-001", "LASER-001"}
TEXT_FIELDS = ("error_code", "symptom", "root_cause", "solution", "verification_result")


def load_cases(path: Path) -> list[dict]:
    cases = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                cases.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {line_number}: invalid JSON: {exc.msg}") from exc
    return cases


def validate_cases(cases: list[dict]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()

    if not cases:
        return ["dataset contains no cases"]

    for index, case in enumerate(cases, start=1):
        label = case.get("case_id", f"row {index}")
        missing = sorted(REQUIRED_FIELDS - case.keys())
        if missing:
            errors.append(f"{label}: missing fields: {', '.join(missing)}")

        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"row {index}: case_id must be a non-empty string")
        elif case_id in seen_ids:
            errors.append(f"{case_id}: duplicate case_id")
        else:
            seen_ids.add(case_id)

        if case.get("synthetic") is not True:
            errors.append(f"{label}: synthetic must be true")

        for field in TEXT_FIELDS:
            value = case.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}: {field} must be a non-empty string")

        if isinstance(case_id, str) and not re.fullmatch(r"SYN-[A-Z]+-[0-9]{3}", case_id):
            errors.append(f"{label}: case_id must match SYN-<TYPE>-<NNN>")

        error_code = case.get("error_code")
        if isinstance(error_code, str) and not re.fullmatch(r"SIM-[A-Z][0-9]{3}", error_code):
            errors.append(f"{label}: error_code must match SIM-<LETTER><NNN>")

        equipment = case.get("equipment")
        if not isinstance(equipment, dict) or equipment.get("id") not in REGISTERED_EQUIPMENT:
            errors.append(f"{label}: equipment.id is not in Equipment_Registry.md")
        elif not isinstance(equipment.get("type"), str) or not equipment["type"].strip():
            errors.append(f"{label}: equipment.type must be a non-empty string")

        for field in ("troubleshooting_steps", "safety_notes", "tags"):
            value = case.get(field)
            if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
                errors.append(f"{label}: {field} must be a non-empty string list")

        for field in ("troubleshooting_steps", "safety_notes"):
            value = case.get(field)
            if isinstance(value, list) and len(value) < 2:
                errors.append(f"{label}: {field} must contain at least two items")

        source = case.get("source")
        if not isinstance(source, dict) or source.get("type") != "synthetic_scenario":
            errors.append(f"{label}: source.type must be synthetic_scenario")
        else:
            if source.get("reference") != "Project Forge synthetic dataset v1":
                errors.append(f"{label}: source.reference must identify dataset v1")
            if "not derived from a customer or OEM record" not in source.get("provenance_note", ""):
                errors.append(f"{label}: source must disclose synthetic provenance")

        review = case.get("review")
        if not isinstance(review, dict) or review.get("status") != "demo_only":
            errors.append(f"{label}: review.status must be demo_only")
        elif review.get("reviewed_by") is not None:
            errors.append(f"{label}: reviewed_by must remain null while status is demo_only")

    covered = {
        case.get("equipment", {}).get("id")
        for case in cases
        if isinstance(case.get("equipment"), dict)
    }
    missing_equipment = sorted(REGISTERED_EQUIPMENT - covered)
    if missing_equipment:
        errors.append(f"dataset does not cover registered equipment: {', '.join(missing_equipment)}")
    return errors


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 1}


def search_cases(cases: list[dict], query: str, limit: int = 3) -> list[tuple[int, dict]]:
    query_tokens = _tokens(query)
    ranked: list[tuple[int, dict]] = []
    for case in cases:
        weighted_text = " ".join(
            [
                case["equipment"]["id"],
                case["equipment"]["type"],
                case["error_code"],
                case["symptom"],
                case["root_cause"],
                " ".join(case["tags"]),
                " ".join(case["tags"]),
            ]
        )
        score = len(query_tokens & _tokens(weighted_text))
        if score:
            ranked.append((score, case))
    return sorted(ranked, key=lambda item: (-item[0], item[1]["case_id"]))[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("dataset", type=Path)
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("dataset", type=Path)
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()

    try:
        cases = load_cases(args.dataset)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors = validate_cases(cases)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if args.command == "validate":
        print(f"VALID: {len(cases)} synthetic cases; {len(REGISTERED_EQUIPMENT)} equipment IDs covered")
        return 0

    matches = search_cases(cases, args.query, args.limit)
    if not matches:
        print("No matching synthetic case found.")
        return 0
    for score, case in matches:
        print(f"[{case['case_id']}] score={score} | {case['equipment']['id']} | {case['symptom']}")
        print(f"Source: {case['source']['reference']} ({case['source']['type']}; demo only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
