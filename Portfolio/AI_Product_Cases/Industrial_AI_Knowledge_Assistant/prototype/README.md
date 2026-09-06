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
- `schema/failure_case.schema.json` — machine-readable JSON Schema contract
- `src/knowledge_demo.py` — validator and deterministic keyword retriever
- `src/evaluate_retrieval.py` — reproducible top-1 retrieval evaluation
- `tests/test_knowledge_demo.py` — schema, coverage, and retrieval tests
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
- Automated tests pass without third-party dependencies.
- The pull request receives a successful `Synthetic dataset checks` workflow run.

## Known limitations

- 10 of the 50 failure cases targeted by Prototype 0.1 are represented.
- Scenarios have not been reviewed by OEM or domain experts.
- Retrieval is deterministic token matching, not embeddings or RAG.
- The 10-query evaluation is curated from the same synthetic records and does not test paraphrase robustness.
- The English-only sample does not validate multilingual behavior.
