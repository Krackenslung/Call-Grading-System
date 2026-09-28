"""Build the grading prompt. The rubric text is inserted verbatim from rubric.md."""

from grader.rubric import Rubric


TRAP_NOTES = {
    "C1": "C1 needs ALL of: company name, the agent's own name, and an offer of help, in the opening. "
    "Missing any one of them caps the score at 5.",
    "C3": "C3 is a gate. Any prohibited statement anywhere in the call (guaranteeing a coverage outcome, "
    "quoting a final binding price as certain before underwriting, giving legal advice) scores 0, "
    "even if the recording disclosure was perfect. Check for prohibited statements before judging the disclosure. "
    "A disclosure that is late or garbled, with no prohibited statement, is 5.",
    "C4": "C4 scores 10 only if the issue is resolved, or the next step names a specific owner AND a timeframe. "
    "A vague next step ('we'll be in touch', 'someone will call you') is 5.",
}

SYSTEM_TEMPLATE = """You are a QA grader for recorded auto-insurance sales and service calls.
Grade the transcript strictly against the rubric below.

<rubric>
{rubric}
</rubric>

How to grade:
- Score only what is in the transcript. Do not infer what happened off-transcript.
- Each criterion is independent.
- Transcripts may be in Spanish, English, or a mix. Grade in the original language; do not
  penalize or reward language choice. Write justifications in English.
- If the call is too short for a criterion to apply fully, grade what the agent did with the
  opportunity they had.
- Allowed scores: {scores}. No other values.
{trap_notes}

For each criterion return:
- score: one of {scores}
- justification: one sentence explaining the score in terms of the rubric level it meets
- evidence: a short VERBATIM quote from the transcript (copied exactly, original language) that
  supports the score, or null if the score is based on something being absent
  (e.g. no recording disclosure)."""


def build_system_prompt(rubric: Rubric) -> str:
    notes = [f"- {TRAP_NOTES[cid]}" for cid in rubric.criteria if cid in TRAP_NOTES]
    scores = ", ".join(str(s) for s in rubric.scores)
    return SYSTEM_TEMPLATE.format(
        rubric=rubric.text.strip(),
        scores=scores,
        trap_notes="\n".join(notes),
    )


def build_user_message(call_id: str, transcript: str) -> str:
    return f"<transcript call_id=\"{call_id}\">\n{transcript.strip()}\n</transcript>"
