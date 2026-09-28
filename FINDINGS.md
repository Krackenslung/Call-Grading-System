# FINDINGS

# Findings

Grader: `claude-opus-5.5`, one call per transcript, graded against C001–C015 (n=15, so each call is ~7 points of agreement). Full tables are in `results/eval.md`. The prompt was **not tuned** on the labels: the rubric notes in it were written before any results existed, so these numbers are a first-run estimate, not a fitted one.

## 1. Headline

|  | C1 | C2 | C3 | C4 | C5 |
| --- | --- | --- | --- | --- | --- |
| Grader exact | 87% | **47%** | 87% | 93% | 80% |
| “Always predict majority” baseline | 80% | 53% | 93% | 53% | 67% |

The grader clearly beats the baseline on **C4 and C5**. It is **below baseline on C2 and C3**. The raw exact rate on C1 and C3 says little, since the labels are nearly constant there. Every disagreement is within ±5 except two severe 0↔︎10 misses, both on C3. Total-score bias is 0.0 because C2 leniency (+1.3) cancels C3 harshness (−1.3): the averages look calibrated while individual criteria are not. All 150 evidence quotes were found verbatim in their transcripts. Self-consistency (repeat runs) was **not** measured.

## 2. The grader’s fault

- **C2 is lenient on service calls (6 of 8 C2 misses are 5→10).** On C002, C005, C008 and C010 it treats verifying the policy number as full discovery (“appropriate to the service nature of the call”). On C003 it credits facts the customer *volunteered*, but the rubric’s 10 requires that the agent “asks questions”. The humans consistently require real probing plus a confirmation. This is the grader’s main systematic error, and the fix is a prompt note (policy or ID verification is not discovery).
- **C009 C5 (human 0, grader 5):** the agent asks “so what was it you were calling about again?” after two off-topic anecdotes. That is “completely loses control of the call”, the rubric’s 0. The grader was too generous.

## 3. Not the grader’s fault

- **C007 C3 (human 10, grader 0, severe):** the transcript has **no recording disclosure anywhere**. The rubric’s C3 0 level says: “No recording disclosure … regardless of everything else.” The human label is wrong. The agent also says the price “es prácticamente el final” (is practically final) right after the underwriting caveat.
- **C009 C1 (human 5, grader 0):** “Thanks for calling, this is Tony.” The company is never named, and the rubric says 0 when the “agent never identifies the company”. The human label is wrong.
- **C012 C1 (human 0, grader 5):** “Gracias por llamar a Seguros Confianza, le atien…” The company is named, then the customer cuts in. Per the rubric, a missing own name is 5, not 0. The human label is inconsistent.
- **C011 C3 (human 10, grader 0, severe) is ambiguous in the rubric.** “La nuestra tiene tiempo de respuesta garantizado” (ours has a guaranteed response time) guarantees roadside *service speed*, not a *coverage outcome*. Both scores are defensible, and QA should decide which reading the rubric intends.
- **C014 C5 / C011 C4 show humans penalising the right error under the wrong criterion.** In C014 the agent confuses the car (“Civic” instead of “Corolla”) and the day (“viernes” instead of “miércoles”). Both sides scored C4 0, but the grader additionally docked C5 while the human docked C2. In C011, the reason for calling was resolved (“ya quedó hecho”, it’s done) and the rubric gives 10 for that. The human’s C4 5 looks like it carries over the pushy upsell, which belongs in C5.

If these three rubric-contradicting labels are corrected, C1 goes to 15/15 and C3 to 14/15.

## 4. When NOT to trust the grader

- **Any C3 = 0 (the gate).** It is the costliest decision and the only one with severe misses. Route every C3 = 0 to a human, with the quoted “prohibited statement” attached.
- **C2 on service and short calls (C028-type)** until the discovery prompt is fixed.
- **Scores that depend on one ambiguous rubric phrase** (“guaranteed” service vs coverage, and which criterion a factual slip belongs to).
- **Its stability is unknown.** Repeat runs should be done before relying on any single score. Code-switching (C003, C011) caused **no** errors in this sample, but n is too small to clear language as a risk.