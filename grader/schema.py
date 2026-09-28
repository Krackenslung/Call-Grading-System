"""Output schema, built from the rubric so criteria and scale are never hardcoded."""

from typing import Any

from pydantic import BaseModel, ValidationError

from grader.rubric import Rubric


class CriterionGrade(BaseModel):
    score: int
    justification: str
    evidence: str | None


def json_schema(rubric: Rubric) -> dict[str, Any]:
    """JSON schema passed to the API as a structured-output constraint."""
    criterion = {
        "type": "object",
        "properties": {
            "score": {"type": "integer", "enum": list(rubric.scores)},
            "justification": {"type": "string"},
            "evidence": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        },
        "required": ["score", "justification", "evidence"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {cid: criterion for cid in rubric.criteria},
        "required": list(rubric.criteria),
        "additionalProperties": False,
    }


def validate(data: Any, rubric: Rubric) -> dict[str, CriterionGrade]:
    """Validate model output. Raises ValueError; never coerces an invalid score."""
    if not isinstance(data, dict):
        raise ValueError(f"expected a JSON object, got {type(data).__name__}")
    missing = set(rubric.criteria) - set(data)
    extra = set(data) - set(rubric.criteria)
    if missing or extra:
        raise ValueError(f"criteria mismatch: missing={sorted(missing)} extra={sorted(extra)}")

    grades = {}
    for cid in rubric.criteria:
        try:
            grade = CriterionGrade.model_validate(data[cid])
        except ValidationError as e:
            raise ValueError(f"{cid}: {e}") from e
        if grade.score not in rubric.scores:
            raise ValueError(f"{cid}: score {grade.score} not in {rubric.scores}")
        grades[cid] = grade
    return grades
