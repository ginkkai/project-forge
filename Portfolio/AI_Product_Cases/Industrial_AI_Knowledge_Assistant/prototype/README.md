# Synthetic Industrial Failure Dataset v1

This package is a small, public-safe dataset and executable retrieval demo for the
Industrial AI Knowledge Assistant prototype.

It turns the repository's data dictionary and equipment registry into one
verifiable loop:

`synthetic cases -> schema validation -> keyword retrieval -> cited result -> measured top-1 accuracy`

## Scope

- 10 synthetic failure cases across all 5 registered equipment types
- No customer, employee, site, or proprietary company data
- Every record carries an explicit synthetic-data flag and provenance note
- Standard-library-only Python; no API key or external service required

The dataset is a prototype artifact, not maintenance guidance. A qualified
technician must verify any real-world action against the applicable OEM manual,
site procedure, and safety requirements.

## Files

- `data/synthetic_failure_cases_v1.jsonl` — one JSON object per failure case
- `data/retrieval_eval_v1.jsonl` — versioned queries and expected case IDs
- `data/retrieval_eval_paraphrase_v1.jsonl` — technician-style paraphrase stress set
- `data/technician_query_review_v1.csv` — controlled annotation template for domain review
- `RETRIEVAL_EVALUATION.md` — metric interpretation, failed cases, and decision gates
- `TECHNICIAN_QUERY_REVIEW.md` — reviewer instructions, privacy boundary, and completion gate
- `schema/failure_case.schema.json` — machine-readable JSON Schema contract
- `src/knowledge_demo.py` — validator and deterministic keyword retriever
- `src/evaluate_retrieval.py` — reproducible top-1 retrieval evaluation
- `src/validate_technician_review.py` — validates review data against the frozen fixture
- `tests/test_knowledge_demo.py` — schema, coverage, and retrieval tests
- `tests/test_technician_review.py` — review-contract and anti-drift tests
- `.github/workflows/synthetic-dataset-checks.yml` — pull-request validation in GitHub Actions

## Record contract

The fields below extend the five failure-case fields in
`Prototype_Data_Dictionary.md` with traceability and governance metadata required
by the PRD.

| Field | Purpose |
|---|---|
| `case_id` | Stable citation identifier |
| `equipment` | Registry ID and equipment type |
| `error_code` | Synthetic alarm or condition code |
| `symptom` | Observable problem |
| `root_cause` | Synthetic diagnosed cause |
| `troubleshooting_steps` | Ordered diagnostic actions |
| `solution` | Synthetic corrective action |
| `verification_result` | Post-action check |
| `safety_notes` | Safety boundary before intervention |
| `source` | Provenance and synthetic-data disclosure |
| `review` | Demonstration-only verification state |
| `tags` | Search terms |

## Run the closed loop

From this directory:

```bash
python src/knowledge_demo.py validate data/synthetic_failure_cases_v1.jsonl
python src/knowledge_demo.py search data/synthetic_failure_cases_v1.jsonl "coolant pressure low"
python src/evaluate_retrieval.py data/synthetic_failure_cases_v1.jsonl data/retrieval_eval_v1.jsonl
python src/evaluate_retrieval.py data/synthetic_failure_cases_v1.jsonl data/retrieval_eval_paraphrase_v1.jsonl --minimum-accuracy 0.6
python src/validate_technician_review.py data/technician_query_review_v1.csv data/retrieval_eval_paraphrase_v1.jsonl
python -m unittest discover -s tests -v
```

The search command prints the matching case ID as a source citation. It does not
generate a diagnosis or claim production-grade semantic retrieval.

## Retrieval evaluation

The versioned evaluation fixture contains one representative query for each of
the 10 synthetic cases. The evaluator reports top-1 accuracy and exits non-zero
when any expected case is not ranked first. On the v1 fixture, the current
deterministic retriever scores **10/10 (100%) top-1 accuracy**.

This is a regression baseline for a deliberately small, synthetic, English-only
fixture. It is not evidence of production accuracy, semantic generalization, or
performance on real technician language. Future retrieval methods should be
compared against the same fixture and then tested on broader reviewed queries.

### Paraphrase stress baseline

A second fixture expresses the same 10 scenarios with technician-style wording
that deliberately avoids many source-record terms. The current keyword retriever
scores **6/10 (60%) top-1 accuracy**. The four misses are versioned as evidence,
not hidden or rewritten to make the metric look better.

The CLI accepts `--minimum-accuracy` so CI can prevent regression below the
recorded 60% baseline while future retrieval methods improve against the same
queries. This threshold is a regression floor, not a production-readiness target.

### Technician review gate

The review template lets a domain reviewer assess whether each stress query is
plausible technician language and whether its expected case is correct. CI locks
the query text and labels to the versioned fixture, validates allowed decisions,
and rejects annotated rows without a reviewer role and date. The template asks
for role only and explicitly excludes names, email addresses, employers, sites,
customer information, and proprietary incident details.

The template is currently blank. It must not be described as technician-reviewed
until all 10 rows pass the validator's `--require-complete` gate and the reviewer
decisions are inspected.

## Automated verification

GitHub Actions runs the validator and all unit tests whenever this prototype or
its workflow changes in a pull request. The workflow uses Python 3.11 and only
standard-library dependencies, so its result is independently reproducible
without credentials or external services.

## Acceptance criteria

- The JSONL file parses and every record satisfies the required contract.
- The documented JSON Schema stays synchronized with the executable validator.
- Case IDs are unique and all records are marked synthetic.
- All five IDs in `Equipment_Registry.md` have at least one case.
- A known symptom query retrieves the intended case and exposes its citation ID.
- The evaluation fixture covers every v1 case and reports 100% top-1 accuracy.
- The paraphrase fixture covers every v1 case and reproduces the documented 60% baseline.
- The technician review template remains aligned to the frozen stress fixture.
- Automated tests pass without third-party dependencies.
- The pull request receives a successful `Synthetic dataset checks` workflow run.

## Known limitations

- 10 of the 50 failure cases targeted by Prototype 0.1 are represented.
- Scenarios have not been reviewed by OEM or domain experts.
- Retrieval is deterministic token matching, not embeddings or RAG.
- The paraphrase stress set is still authored from synthetic records and has not been reviewed by technicians.
- The technician review template is an uncompleted review instrument, not review evidence.
- Current paraphrase top-1 accuracy is only 60%, confirming weak lexical generalization.
- The English-only sample does not validate multilingual behavior.
