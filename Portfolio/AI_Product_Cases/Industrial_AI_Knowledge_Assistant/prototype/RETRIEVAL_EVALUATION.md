# Retrieval Evaluation Card

## Purpose

This card documents the retrieval evidence for the Synthetic Industrial Failure
Dataset v1. It separates a regression check from a robustness check so the
headline metric cannot be interpreted as production accuracy.

## Evaluated system

- Method: deterministic token-overlap ranking
- Dataset: 10 synthetic failure cases across 5 registered equipment types
- Output: top-ranked case ID used as a citation
- External services, embeddings, and LLMs: none

## Evaluation sets

| Fixture | Intent | Queries | Relationship to source records |
|---|---|---:|---|
| `retrieval_eval_v1.jsonl` | Exact-term regression | 10 | Reuses terminology from the synthetic records |
| `retrieval_eval_paraphrase_v1.jsonl` | Technician-style paraphrase stress | 10 | Rewords each scenario and removes many source terms |

Both fixtures cover all 10 case IDs exactly once. Both were authored from the
same synthetic records and have not been reviewed by working technicians.

## Results

| Fixture | Top-1 result | Interpretation |
|---|---:|---|
| Exact-term regression | 10/10 (100%) | The implementation reproduces known lexical lookups |
| Paraphrase stress | 6/10 (60%) | The implementation does not generalize reliably to reworded symptoms |

The four paraphrase misses are:

| Expected case | Scenario |
|---|---|
| `SYN-COMP-001` | Compressor cannot reach target pressure under high demand |
| `SYN-INSPECT-002` | Probe qualification fails after restart |
| `SYN-LASER-001` | Marking contrast becomes weak |
| `SYN-LASER-002` | Marking position shifts after fixture change |

## Failure interpretation

The observed failures are consistent with the known limits of token-overlap
retrieval:

- synonyms such as “psi,” “reboot,” “pale,” and “nest” are not mapped to the
  vocabulary used by the records;
- generic shared words can outrank the intended case;
- deterministic case-ID tie-breaking can select the wrong record when lexical
  scores are equal;
- the retriever has no semantic model, domain ontology, or equipment-aware
  filtering.

These are hypotheses grounded in the implementation and failed queries. They are
not evidence from field users.

## Reproduction

From the prototype directory:

```bash
python src/evaluate_retrieval.py data/synthetic_failure_cases_v1.jsonl data/retrieval_eval_v1.jsonl
python src/evaluate_retrieval.py data/synthetic_failure_cases_v1.jsonl data/retrieval_eval_paraphrase_v1.jsonl --minimum-accuracy 0.6
```

The 60% minimum is a regression floor: future changes must not make the current
stress result worse. It is not an acceptance threshold for production use.

## Decision gates

Before claiming retrieval robustness:

1. A domain reviewer must confirm that the stress queries resemble plausible
   technician language.
2. The fixed paraphrase set must remain unchanged while candidate retrieval
   methods are compared.
3. A separate, previously unseen query set must be created after method
   selection to detect overfitting.
4. Multilingual and real maintenance queries must be evaluated separately.

Until those gates are met, the prototype demonstrates a reproducible retrieval
experiment, not a deployable troubleshooting system.
