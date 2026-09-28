"""Grade all 30 calls, write results/grades.json, print the evaluation.

    python run.py              # uses cached responses when available
    python run.py --regrade    # ignore the cache, call the model again
    python run.py --eval-only  # re-evaluate existing results/grades.json
    MOCK=1 python run.py       # replay cache only; fails on a cache miss
"""

import argparse
import json
import sys

import evaluate
from grader import config
from grader.grade import grade_call
from grader.rubric import load_rubric


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--regrade", action="store_true", help="ignore cached responses")
    parser.add_argument("--eval-only", action="store_true", help="skip grading")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8") 

    if not args.eval_only:
        if args.regrade and config.MOCK:
            sys.exit("--regrade and MOCK=1 contradict each other.")
        rubric = load_rubric()
        print(f"Rubric: {', '.join(rubric.criteria)} scored {rubric.scores}. "
              f"Model: {config.MODEL}{' (MOCK: cache only)' if config.MOCK else ''}")
        results = []
        for call_id in config.CALL_IDS:
            result = grade_call(call_id, rubric, regrade=args.regrade)
            status = f"total {result['total']}" if result["status"] == "ok" else "FAILED: " + "; ".join(result["errors"])
            print(f"  {call_id}: {status}")
            results.append(result)
        config.RESULTS_DIR.mkdir(exist_ok=True)
        config.GRADES_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {config.GRADES_PATH}\n")

    evaluate.main()


if __name__ == "__main__":
    main()
