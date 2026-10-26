# Industrial AI Knowledge Assistant — Synthetic Retrieval Evidence Case

## Portfolio summary

This case demonstrates how a product manager can turn an industrial knowledge
assistant concept into a small, testable evidence loop before investing in a
full RAG stack. The prototype uses public-safe synthetic failure cases, a
machine-readable contract, deterministic retrieval, two evaluation sets, and a
controlled domain-review gate.

**Status:** prototype evidence, not a deployable maintenance system  
**Role:** product owner and prototype builder  
**Domain:** industrial equipment knowledge retrieval  
**Repository asset:** `prototype/` in the Industrial AI Knowledge Assistant case

## Problem

Industrial service teams need fast access to failure cases, but a convincing
demo must answer more than “can it return text?” It must show:

1. where each answer came from;
2. whether the data contract is consistent;
3. whether retrieval survives realistic rewording;
4. what has and has not been reviewed by domain experts; and
5. how a future method can be compared without rewriting the test.

The initial PRD targets 50 failure cases and an eventual RAG experience. This
iteration deliberately narrows the scope to 10 synthetic cases so the complete
evidence path can be executed and audited first.

## Product hypothesis

> A small, traceable retrieval prototype with explicit failure evidence is more
> valuable than a larger unmeasured demo because it reveals the real next risk:
> query generalization and domain validity.

## Minimum closed loop

`synthetic cases -> schema/provenance validation -> retrieval -> case-ID citation -> fixed evaluation -> domain-review instrument -> CI`

The package contains:

- 10 explicitly synthetic failure cases covering 5 registered equipment types;
- a JSON Schema and executable validator;
- deterministic token-overlap retrieval with case-ID citations;
- a 10-query exact-term regression fixture;
- a 10-query technician-style paraphrase stress fixture;
- a review form, strict completion validator, and privacy-safe review summary;
- standard-library tests and GitHub Actions verification.

## Key product decisions

| Decision | Why it matters | Trade-off |
|---|---|---|
| Synthetic, public-safe data only | Makes the artifact shareable without exposing customers, sites, employees, credentials, or proprietary incidents | Does not establish field validity |
| Stable case IDs in every result | Makes retrieval outputs auditable and citable | Does not guarantee the case itself is correct |
| Freeze evaluation queries | Prevents improving the headline metric by rewriting failed tests | A small fixed set can still be overfit |
| Separate exact-term and paraphrase sets | Distinguishes implementation regression from language robustness | Both sets were derived from the same synthetic records |
| Preserve the 60% stress result | Turns failure into decision evidence instead of hiding it | The public score is intentionally imperfect |
| Human review gate before optimization | Avoids tuning to queries that may not resemble real technician language | Progress depends on an external reviewer |

## Evidence and results

| Evidence | Result | Correct interpretation |
|---|---:|---|
| Dataset validation | 10 valid synthetic cases; 5/5 equipment IDs covered | Contract and declared coverage are reproducible |
| Exact-term retrieval | 10/10 top-1 (100%) | Known lexical lookups are reproduced |
| Paraphrase stress retrieval | 6/10 top-1 (60%) | Token overlap does not generalize reliably to reworded symptoms |
| Automated verification | 25 unit tests plus GitHub Actions | Current behavior and safety boundaries are regression-tested |
| Technician review | Not completed | No claim of technician, OEM, or field validation is permitted |

The four paraphrase misses involve compressor pressure, inspection-probe
qualification, laser-mark contrast, and laser-mark position. The failure pattern
is consistent with missing synonym handling, generic-word collisions, tie
breaking, and lack of equipment-aware or semantic retrieval. These are
implementation-grounded hypotheses, not field-user findings.

## What the evidence changed

The exact-term result alone could have supported a misleading “100% accuracy”
claim. The paraphrase fixture changed the product decision: retrieval should not
be optimized yet. First, a working technician must confirm that the 10 stress
queries are plausible and that their expected cases are correctly labeled.

That review is controlled by three safeguards:

1. query text and expected case IDs are locked to the frozen fixture;
2. names, email addresses, employers, sites, customers, and proprietary incident
   details are excluded; and
3. incomplete reviews cannot be summarized as evidence.

## Safety and claim boundary

This artifact is not maintenance guidance. It does not demonstrate production
accuracy, multilingual performance, semantic generalization, OEM validation,
or real technician usefulness. Any real-world action must be checked against
the applicable OEM manual, site procedure, and safety requirements.

## Reproduce the evidence

From the prototype directory:

```bash
python src/knowledge_demo.py validate data/synthetic_failure_cases_v1.jsonl
python src/evaluate_retrieval.py data/synthetic_failure_cases_v1.jsonl data/retrieval_eval_v1.jsonl
python src/evaluate_retrieval.py data/synthetic_failure_cases_v1.jsonl data/retrieval_eval_paraphrase_v1.jsonl --minimum-accuracy 0.6
python src/validate_technician_review.py data/technician_query_review_v1.csv data/retrieval_eval_paraphrase_v1.jsonl
python -m unittest discover -s tests -v
```

## Next decision gate

Ask one qualified maintenance technician to complete all 10 review rows. If the
strict validator passes, generate the privacy-safe summary and inspect rejected
or uncertain queries. Only then select and compare the next retrieval method
against the unchanged fixture.

## Interview discussion prompts

- Why was the 60% result preserved instead of immediately tuned away?
- How does the review contract prevent metric gaming and false expert claims?
- Which risks require better retrieval, and which require better source data?
- What new evidence would justify moving from keyword retrieval to embeddings
  or RAG?

