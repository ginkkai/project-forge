# Synthetic Industrial Failure Dataset v1

This package is a small, public-safe dataset and executable retrieval demo for the
Industrial AI Knowledge Assistant prototype.

It turns the repository's data dictionary and equipment registry into one
verifiable loop:

`synthetic cases -> schema validation -> keyword retrieval -> cited result`

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
- `src/knowledge_demo.py` — validator and deterministic keyword retriever
- `tests/test_knowledge_demo.py` — schema, coverage, and retrieval tests

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
python -m unittest discover -s tests -v
```

The search command prints the matching case ID as a source citation. It does not
generate a diagnosis or claim production-grade semantic retrieval.

## Acceptance criteria

- The JSONL file parses and every record satisfies the required contract.
- Case IDs are unique and all records are marked synthetic.
- All five IDs in `Equipment_Registry.md` have at least one case.
- A known symptom query retrieves the intended case and exposes its citation ID.
- Automated tests pass without third-party dependencies.

## Known limitations

- 10 of the 50 failure cases targeted by Prototype 0.1 are represented.
- Scenarios have not been reviewed by OEM or domain experts.
- Retrieval is deterministic token matching, not embeddings or RAG.
- The English-only sample does not yet validate multilingual behavior.

