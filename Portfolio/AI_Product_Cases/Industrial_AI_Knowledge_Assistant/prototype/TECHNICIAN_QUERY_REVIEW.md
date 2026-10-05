# Technician Query Review Pack v1

## Purpose

This pack turns the 10-query paraphrase stress set into a controlled domain-review task.
It asks a working technician or maintenance-domain reviewer to judge the language and
the intended case mapping without changing the frozen evaluation fixture.

The review is about query realism and label correctness. It is not an OEM validation of
the synthetic troubleshooting content and does not make the prototype safe for field use.

## Reviewer instructions

Open `data/technician_query_review_v1.csv` and complete these fields for every row:

| Field | Allowed value | Meaning |
|---|---|---|
| `plausible_technician_language` | `yes`, `no`, `uncertain` | Would a technician plausibly describe the symptom this way? |
| `expected_case_correct` | `yes`, `no`, `uncertain` | Does the query point to the listed synthetic case? |
| `corrected_query` | free text | Required when language is marked `no` |
| `corrected_case_id` | case ID | Required when the expected case is marked `no` |
| `reviewer_role` | free text | Role only; do not enter a personal name, email, employer, or site |
| `review_date` | `YYYY-MM-DD` | Date of the review |
| `notes` | free text | Optional reasoning; do not include customer or proprietary data |

Do not edit `query_id`, `query`, or `expected_case_id`. These columns are locked to the
versioned stress fixture so the review cannot silently rewrite failed queries after seeing
the 60% result.

## Validation

The blank template is checked in CI:

```bash
python src/validate_technician_review.py \
  data/technician_query_review_v1.csv \
  data/retrieval_eval_paraphrase_v1.jsonl
```

After a reviewer completes all 10 rows, use the stricter gate:

```bash
python src/validate_technician_review.py \
  data/technician_query_review_v1.csv \
  data/retrieval_eval_paraphrase_v1.jsonl \
  --require-complete
```

A passing completed review means only that every query received a traceable decision and
that the frozen fixture was not changed. It does not imply agreement, retrieval quality,
or production readiness.
