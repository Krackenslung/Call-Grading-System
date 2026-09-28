# CLAUDE.md

Context for AI assistants working in this repo. Read this before making changes.

## What this is

A 4-hour take-home prototype for Confie AI Engineering: an LLM-based grader for auto-insurance call transcripts, plus an evaluation of whether it can be trusted.

The evaluators weight things in this order:
1. Evaluation design and findings (when should the grader NOT be trusted?)
2. How disagreement with human labels is handled
3. A live 30-min session where they change something and I adapt it
4. Code quality proportionate to a 4-hour prototype

**Agreement % alone is not the goal.** A sharp explanation of disagreements beats a high number. Optimize for clarity and defensibility, not cleverness.

## Hard constraints

- **Time cap: 4 hours total.** Don't gold-plate. No UI, no exhaustive tests, no abstractions "for later".
- **One-command run** must grade all 30 calls and print the evaluation.
- Required outputs: `results/grades.json`, `FINDINGS.md` (half page, max one), README with actual time spent and "what I'd build next with one more day".
- All data is synthetic. Never add real customer data.
- Must work without a paid API key: support a mock/cached mode.

## Inputs

- `transcripts/C001.txt` … `C030.txt` — Spanish, English, or mixed
- `rubric.md` — 5 criteria (C1–C5), each scored 0, 5, or 10
- `labels.csv` — human grades for C001–C015 only (columns: `call_id,c1_greeting,c2_discovery,c3_compliance,c4_resolution,c5_professionalism,total`). C016–C030 are unlabeled.

## Layout

```
grader/
  config.py      # model, criteria list, paths — single source of truth
  prompt.py      # builds the prompt from rubric.md (do NOT hardcode rubric text)
  schema.py      # pydantic models; scores constrained to {0, 5, 10}
  grade.py       # transcript -> validated JSON; caches raw responses
evaluate.py      # agreement metrics vs labels.csv, confusion matrices, disagreement table
run.py           # entry point: grade all 30, write results, print eval
results/
  grades.json    # final output for all 30 calls
  raw/           # cached raw LLM responses, keyed by call_id + prompt hash
  eval.md        # generated evaluation report
FINDINGS.md
README.md
Makefile
```

## Commands

```bash
make run          # grade all 30 (uses cache when available) + print evaluation
make eval         # re-run evaluation only, from results/grades.json
make regrade      # ignore cache, call the model again
MOCK=1 make run   # no API key: replay results/raw/ only; fail loudly on cache miss
```

API key via `ANTHROPIC_API_KEY` env var (never commit it). Model string lives in `grader/config.py`.

## Grader design rules

- **Rubric is loaded, not hardcoded.** The live session will likely change the rubric (new criterion, changed threshold, different scale). Criteria names and allowed scores come from config + `rubric.md`, so a change is a one-file edit.
- **Structured output, validated.** Each criterion returns `{score, justification, evidence}`. `evidence` is a short verbatim quote from the transcript (or `null` if the score is based on absence, e.g. no recording disclosure). Reject/retry once on invalid JSON or a score outside {0,5,10}; after that, record the failure explicitly instead of guessing.
- **Reproducible via cache, not sampling.** The model (`claude-opus-5-5`) rejects `temperature`, so don't set it. Cache every raw response (keyed by model + effort + prompt + schema hash) so reruns are free and the live demo is reproducible.
- **Language-agnostic.** Don't translate transcripts first; grade in the original language. Justifications in English.
- **One call per transcript** grading all criteria is fine for the prototype. Note per-criterion calls as a possible improvement if cross-criterion contamination shows up.

### Rubric traps to encode explicitly in the prompt

- **C3 is a gate:** any prohibited statement (guaranteeing coverage outcome, quoting a final binding price before underwriting, legal advice) → 0, regardless of disclosure quality. Disclosure late/mangled → 5.
- **C1** requires company name AND agent's own name AND offer of help, in the opening.
- **C4** needs a specific owner AND timeframe for a 10. "We'll be in touch" is a 5.
- Score only what's in the transcript. Don't infer off-transcript behavior.
- Short calls: grade what the agent did with the opportunity they had.

## Evaluation rules

- Report **per criterion**, not just overall: exact match, within-5 agreement (adjacent), and a 3×3 confusion matrix.
- Also report total-score MAE and bias (grader mean − human mean) per criterion: is the grader systematically harsh or lenient?
- **Be honest about n=15.** Kappa on this set is unstable, and some criteria are nearly constant in the labels (C3 is 10 on 14/15 calls). Report kappa if used, but flag when it's meaningless; don't let a headline number hide that.
- **Severity matters more than distance.** A 10↔0 miss on C3 (compliance) is worse than a 5↔10 miss on C5. Call out 10↔0 disagreements individually.
- **Don't overfit to the calibration set.** If the prompt is tuned by looking at C001–C015 disagreements, say so in FINDINGS and treat the reported agreement as optimistic. Ideally tune on a subset and report on the rest.
- For every disagreement, `evaluate.py` prints: call_id, criterion, human score, grader score, grader justification + evidence — so FINDINGS can be written from it directly.

## FINDINGS.md structure

Half a page. Cite call IDs.
1. Headline: where the grader agrees and where it doesn't (per criterion).
2. Grader's fault: misread rubric, missed evidence, hallucinated evidence, language issue.
3. Not the grader's fault: label looks inconsistent with the rubric, rubric is ambiguous, transcript is genuinely borderline. Argue it from rubric text, don't just assert.
4. When NOT to trust the grader (e.g. C3 gate decisions, very short calls, heavy code-switching) and what a human should review.

## Code style

- Python 3.11+, standard library + `anthropic`, `pydantic`, `pandas` (or stdlib csv), `scikit-learn` only if kappa is used. Nothing else without a reason.
- Small functions, clear names, type hints. No classes unless they earn it.
- Fail loudly: missing transcript, bad label row, invalid model output → clear error, not a silent default.
- Comments explain *why*, not *what*.

## Don't

- Don't hardcode rubric text or criterion names in multiple places.
- Don't silently coerce invalid scores (e.g. a 7 → 5).
- Don't report a single overall agreement number without the per-criterion breakdown.
- Don't spend time on UI, packaging, or test coverage beyond a smoke test.
- Don't commit API keys or anything in `.env`.
