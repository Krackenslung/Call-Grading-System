"""Transcript -> validated grades. Every raw API response is cached on disk."""

import hashlib
import json
import re
from typing import Any

from grader import config
from grader.prompt import build_system_prompt, build_user_message
from grader.rubric import Rubric
from grader.schema import json_schema, validate

MAX_ATTEMPTS = 2  


def load_transcript(call_id: str) -> str:
    path = config.TRANSCRIPTS_DIR / f"{call_id}.txt"
    if not path.exists():
        raise FileNotFoundError(f"missing transcript: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"empty transcript: {path}")
    return text


def _prompt_hash(system: str, user: str, schema: dict) -> str:
    key = json.dumps([config.MODEL, config.EFFORT, system, user, schema], sort_keys=True)
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]


def _call_api(system: str, user: str, schema: dict) -> dict[str, Any]:
    import anthropic 

    client = anthropic.Anthropic(max_retries=6)
    response = client.messages.create(
        model=config.MODEL,
        max_tokens=config.MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_config={"effort": config.EFFORT, "format": {"type": "json_schema", "schema": schema}},
    )
    text = "".join(b.text for b in response.content if b.type == "text")
    return {
        "model": response.model,
        "stop_reason": response.stop_reason,
        "text": text,
        "usage": {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens},
    }


def _get_raw(call_id: str, phash: str, attempt: int, system: str, user: str, schema: dict, regrade: bool) -> dict:
    path = config.RAW_DIR / f"{call_id}.{phash}.a{attempt}.json"
    if path.exists() and not regrade:
        return json.loads(path.read_text(encoding="utf-8"))
    if config.MOCK:
        raise RuntimeError(
            f"MOCK=1 but no cached response for {call_id} (attempt {attempt}, prompt hash {phash}). "
            f"Expected {path}. Run once with an API key, or the prompt/rubric changed since caching."
        )
    raw = _call_api(system, user, schema)
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    return raw


def _normalize(s: str) -> str:
    s = s.casefold()
    s = re.sub(r"[\"'“”‘’«»]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def evidence_found(evidence: str | None, transcript: str) -> bool | None:
    """True if the quote really appears in the transcript. None when no quote was given.

    A False here is a hallucinated or paraphrased quote: the score may still be right,
    but the grader's stated reason cannot be checked.
    """
    if evidence is None:
        return None
    haystack = _normalize(transcript)
    # Models often elide with "..." inside a quote; each fragment must appear.
    fragments = [f for f in (_normalize(p) for p in re.split(r"\.\.\.|…", evidence)) if f]
    return bool(fragments) and all(f in haystack for f in fragments)


def grade_call(call_id: str, rubric: Rubric, regrade: bool = False) -> dict[str, Any]:
    transcript = load_transcript(call_id)
    system = build_system_prompt(rubric)
    user = build_user_message(call_id, transcript)
    schema = json_schema(rubric)
    phash = _prompt_hash(system, user, schema)

    errors = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        raw = _get_raw(call_id, phash, attempt, system, user, schema, regrade)
        try:
            if raw["stop_reason"] not in ("end_turn", "stop_sequence"):
                raise ValueError(f"stop_reason={raw['stop_reason']}")
            grades = validate(json.loads(raw["text"]), rubric)
        except (ValueError, json.JSONDecodeError) as e:
            errors.append(f"attempt {attempt}: {e}")
            continue
        return {
            "call_id": call_id,
            "status": "ok",
            "grades": {
                cid: {**g.model_dump(), "evidence_found": evidence_found(g.evidence, transcript)}
                for cid, g in grades.items()
            },
            "total": sum(g.score for g in grades.values()),
            "model": raw["model"],
            "prompt_hash": phash,
            "attempts": attempt,
        }

    return {"call_id": call_id, "status": "failed", "errors": errors, "prompt_hash": phash}
