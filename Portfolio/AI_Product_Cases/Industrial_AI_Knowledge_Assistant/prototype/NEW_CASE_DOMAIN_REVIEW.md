# New Case Domain Review v1

This review pack covers only the five cases added when the public synthetic
dataset expanded from 10 to 15 records. It does not replace the separate
technician-language review of the frozen 10-query paraphrase fixture.

## Review purpose

A qualified industrial maintenance or equipment-domain reviewer should assess
each new synthetic case for:

1. technical plausibility of the symptom and scenario;
2. plausibility of the proposed root cause;
3. safety of the troubleshooting sequence; and
4. adequacy of the stated safety boundary.

Use `yes`, `no`, or `uncertain` for each decision. Set `correction_required` to
`yes` whenever any decision is `no`, and describe the required correction in
`review_notes`. The notes must not contain names, email addresses, employers,
customers, sites, real incident details, credentials, or proprietary data.

## Anti-drift control

Each row contains a SHA-256 fingerprint of the case ID, equipment, symptom,
root cause, troubleshooting steps, solution, verification result, and safety
notes. The validator rejects the review if any reviewed case changes afterward.
This prevents a completed review from being attached to different content.

## Reviewer metadata

Record only a general role, such as `maintenance technician`, and an ISO date
(`YYYY-MM-DD`). Do not record the reviewer's identity or organization.

## Validation

From the prototype directory:

```bash
python src/validate_new_case_review.py \
  data/new_case_domain_review_v1.csv \
  data/synthetic_failure_cases_v1.jsonl
```

The blank template must pass normal validation. After every row is completed,
run the strict gate:

```bash
python src/validate_new_case_review.py \
  data/new_case_domain_review_v1.csv \
  data/synthetic_failure_cases_v1.jsonl \
  --require-complete
```

Until the strict gate passes and corrections are resolved, the five cases must
remain labelled synthetic and unreviewed. A completed form supports only the
reviewed fields; it does not establish OEM validation, production accuracy, or
maintenance guidance.
