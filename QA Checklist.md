# QA Checklist

Done: No

#### 1. Evaluation design (highest weight)

- [x]  Metrics are chosen **and justified** in writing, not just computed. For example: exact match, off-by-one (±5), quadratic-weighted Cohen's kappa, per-criterion breakdown.
- [x]  You report agreement **per criterion**, not only an overall number, since one weak criterion can hide inside a good average.
- [x]  You include a confusion matrix (or a simple 0/5/10 × 0/5/10 table) per criterion, so you can see whether the grader skews high or low.
- [x]  You acknowledge the small sample size: n=15 means every call is about 6.7%, so you avoid overclaiming precision.
- [x]  You check the baseline. What agreement would "always predict the majority score" get? If your grader barely beats it, say so.
- [x]  You run the grader 2–3 times on the calibration set to check **self-consistency**. If it disagrees with itself, that's a trust signal on its own.
- [x]  The prompt wasn't tuned on C001–C015 in a way that leaks the labels. If you iterated against them, you say so.
- [x]  The evaluation script prints results when the one-command run finishes.

#### 2. Results & disagreement handling

- [x]  Every disagreement on C001–C015 is listed with call ID, criterion, human score, grader score, and the grader's justification.
- [x]  Each disagreement is classified. Common buckets:
    - The grader was wrong (misread, hallucinated evidence, or missed something)
    - The human label looks questionable, backed by transcript evidence
    - The rubric is ambiguous, so both scores are defensible
    - A language or code-switching issue
- [x]  Claims that a human was wrong **cite the transcript line**. Never just assert it.
- [x]  You include a clear "**when NOT to trust the grader**" section, covering specific conditions like language mix, call type (sales vs. service), long calls, or particular criteria.
- [x]  You recommend what should go to human review. For example: low-confidence scores, specific criteria, or calls where repeated runs disagree.
- []  `FINDINGS.md` fits within about half a page to one page. Be sharp, not exhaustive.

#### 3. Functionality (the grader)

- [x]  It grades all 30 calls, C001–C030.
- [x]  It outputs exactly the 5 rubric criteria, each scored only 0, 5, or 10.
- [x]  Each criterion has a one-line justification that ideally references the transcript.
- [x]  The rubric text is loaded from `rubric.md` rather than hardcoded. The live session may well change the rubric.
- [x]  It handles Spanish, English, and mixed calls. Spot-check a few of each.
- [x]  Temperature is 0, or set low, for reproducibility.
- []  `FINDINGS.md` exists, is complete, and is committed.

#### 4. Output validation

- [x]  JSON is validated against a schema (Pydantic or similar): correct criterion names, allowed values {0, 5, 10}, and a non-empty justification.
- [x]  Out-of-range scores like 7 or "10/10" are rejected or normalized explicitly, never silently.
- [x]  A missing criterion causes a clear failure, not a silent default to 0.

#### 5. Error handling & robustness

- [x]  API failures (timeout, rate limit, 5xx) are retried with backoff.
- [x]  Malformed model output triggers a retry or re-prompt, then is marked as failed.
- [x]  One bad transcript doesn't crash the whole run. It gets logged and the run continues.
- [x]  Failed or ungraded calls show up clearly in the output and are excluded from metrics with a note.
- [x]  Empty, very short, or very long transcripts are handled (context limits).
- [x]  Transcripts are read as UTF-8 so Spanish accents and ñ survive.
- [x]  A missing API key produces a clear error message. If you mock the calls, the mock mode is documented.
- [x]  Optional: responses are cached, so re-runs are fast and cheap during the live session.

#### 6. Reproducibility & the one-command run

- [x]  You tested `docker compose up` / `make run` / the script from a **fresh clone**, not just your working directory.
- [x]  Dependencies are pinned (`requirements.txt` or lockfile).
- [x]  A `.env.example` is included, and the real `.env` is in `.gitignore`.
- [x]  The model name and version are recorded in the output or README.
- [x]  The run finishes in a reasonable time. Note how long it takes.

#### 7. Code quality

- [x]  Code is separated simply: loading, grading, evaluation, and reporting.
- [x]  Nothing is dead: no commented-out experiments or unused files.
- [x]  Names are clear, with a few comments where decisions aren't obvious.
- [x]  Clean beats clever, so nothing is over-engineered for a 4-hour prototype.

#### 8. Live session readiness

- [x]  You can explain every line, including code AI wrote for you.
- [x]  Practice quick changes:
    - Add, remove, or reword a rubric criterion
    - Swap the model or provider
    - Change the scoring scale (e.g., 0–5)
    - Add a new metric
    - Grade a single new transcript
- [x]  Config values (model, paths, temperature) live in one place.
- [x]  It runs on your own machine with your keys and has been tested recently.

#### 9. Deliverables & honesty

- [x]  The README has exact run steps, **actual time spent**, and where you stopped.
- [x]  You have a "what I'd build next with one more day" note. For example: confidence scoring, evidence quotes per criterion, a larger calibration set, inter-rater comparison, or human review routing.
- [x]  Any mocked calls or free-tier limitations are disclosed.
- [x]  No secrets are anywhere in the git history.
- []  The repo link opens correctly, and all files are present: code, `FINDINGS.md`, `results/eval.md`, and the README.