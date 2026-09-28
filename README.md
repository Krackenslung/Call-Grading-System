# Call Grading System

An LLM grader for auto-insurance call transcripts, plus an evaluation of how far it can be trusted against human labels.

## Run

```bash
python -m venv .venv
.venv/Scripts/activate            # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt

export ANTHROPIC_API_KEY=...      # PowerShell: $env:ANTHROPIC_API_KEY="..."
python run.py                     # grade all 30 calls, write results/, print the evaluation
```

| Command | `make` equivalent | What it does |
|---|---|---|
| `python run.py` | `make run` | Grade all 30 calls (cache first), then evaluate |
| `python run.py --eval-only` | `make eval` | Re-evaluate `results/grades.json` only |
| `python run.py --regrade` | `make regrade` | Ignore the cache and call the model again |
| `MOCK=1 python run.py` | `MOCK=1 make run` | No API key: replay `results/raw/` only; fails on a cache miss |

## Outputs

- `results/grades.json`: per call and per criterion, the score, a one-line justification, a verbatim `evidence` quote (or `null` when the score rests on something missing), and `evidence_found`, which checks whether that quote really appears in the transcript.
- `results/eval.md`: agreement report on C001–C015 (the same text is printed to the console).
- `results/raw/`: cached raw model responses, keyed by call ID and a hash of model, effort, prompt and schema.
- `FINDINGS.md`: analysis of the disagreements.

## Design choices

- **The rubric is parsed, not hardcoded.** Criteria (`## C1. Name`) and the score scale (`scored **0, 5, or 10**`) are read from `rubric.md`. Label columns are matched by prefix (`c1_…`). Adding a criterion means editing the rubric and adding a label column.
- **Structured output plus validation.** The API is constrained to a JSON schema built from the rubric, and the output is validated again with pydantic. Invalid output gets one retry; after that the call is recorded as `failed`. Scores are never coerced.
- **Reproducibility.** Opus 5.5 does not accept `temperature`, so reruns are made reproducible by caching every raw response. Any change to the prompt or rubric changes the hash, which forces a fresh call.
- **Metrics.** Each criterion gets exact match, within ±5, a count of 0↔10 misses, bias, a confusion matrix and linear-weighted κ. κ is flagged as unstable when the human labels are ≥80% one value, as C3 is (14/15 are 10). Totals get MAE and bias. There is also a tune (C001–C007) vs holdout (C008–C015) split, so any prompt tuning I do can be reported honestly.

## Time spent

25 minutes Reading brief.md, rubric.md, labels.csv and understanding project 
20 minutes Designed check list to qa and make sure project does what is expected 
10 minutes Designing arquitecture and claude file 
15 minutes Generated graeder with Claude code made project, added Claude API key 
25 minuets Ran Manually filling checklist for qa
15 minutes Ran program and verified results
20 minutes Documentation of project 

## What I'd build next with one more day


