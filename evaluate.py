"""Compare results/grades.json to labels.csv and write results/eval.md.

Run standalone to re-evaluate without regrading: python evaluate.py
"""

import csv
import json
import sys
from collections import Counter
from statistics import mean

from grader import config
from grader.rubric import Rubric, load_rubric

# Kappa is reported but flagged when the human labels barely vary: with n=15 and one
# class covering most calls, a single disagreement swings it wildly.
KAPPA_DOMINANT_SHARE = 0.8


def load_labels(rubric: Rubric) -> dict[str, dict[str, int]]:
    """{call_id: {"C1": 10, ...}}. Columns are matched to criteria by prefix (c1_ -> C1)."""
    with config.LABELS_PATH.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        columns = {}
        for cid in rubric.criteria:
            matches = [c for c in reader.fieldnames if c.lower().startswith(cid.lower() + "_")]
            if len(matches) != 1:
                raise ValueError(f"{config.LABELS_PATH}: expected one column for {cid}, found {matches}")
            columns[cid] = matches[0]

        labels = {}
        for row in reader:
            call_id = row["call_id"].strip()
            scores = {}
            for cid, col in columns.items():
                value = int(row[col])
                if value not in rubric.scores:
                    raise ValueError(f"{config.LABELS_PATH}: {call_id} {col}={value} not in {rubric.scores}")
                scores[cid] = value
            if "total" in row and int(row["total"]) != sum(scores.values()):
                raise ValueError(f"{config.LABELS_PATH}: {call_id} total {row['total']} != sum {sum(scores.values())}")
            labels[call_id] = scores
    return labels


def weighted_kappa(human: list[int], grader: list[int], scale: tuple[int, ...]) -> float | None:
    """Linear-weighted Cohen's kappa. None when undefined (no variation at all)."""
    idx = {s: i for i, s in enumerate(scale)}
    k, n = len(scale), len(human)
    w = [[abs(i - j) / (k - 1) for j in range(k)] for i in range(k)]
    obs = [[0.0] * k for _ in range(k)]
    for h, g in zip(human, grader):
        obs[idx[h]][idx[g]] += 1 / n
    ph = [sum(row) for row in obs]
    pg = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    observed = sum(w[i][j] * obs[i][j] for i in range(k) for j in range(k))
    expected = sum(w[i][j] * ph[i] * pg[j] for i in range(k) for j in range(k))
    return None if expected == 0 else 1 - observed / expected


def confusion(human: list[int], grader: list[int], scale: tuple[int, ...]) -> list[str]:
    counts = Counter(zip(human, grader))
    lines = ["| human \\ grader | " + " | ".join(str(s) for s in scale) + " |",
             "|---|" + "---|" * len(scale)]
    for h in scale:
        lines.append(f"| **{h}** | " + " | ".join(str(counts[(h, g)]) for g in scale) + " |")
    return lines


def pct(x: int, n: int) -> str:
    return f"{x}/{n} ({100 * x / n:.0f}%)" if n else "n/a"


def evaluate(grades: dict[str, dict], labels: dict[str, dict[str, int]], rubric: Rubric) -> str:
    scale = rubric.scores
    step = min(b - a for a, b in zip(scale, scale[1:]))
    worst = scale[-1] - scale[0]
    out = ["# Evaluation: grader vs human labels", ""]

    failed = [cid for cid, g in grades.items() if g["status"] != "ok"]
    labeled = [cid for cid in sorted(labels) if cid in grades and grades[cid]["status"] == "ok"]
    missing = [cid for cid in sorted(labels) if cid not in labeled]
    out.append(f"Labeled calls compared: **{len(labeled)}** "
               f"(model: {next((g['model'] for g in grades.values() if g['status'] == 'ok'), 'n/a')})")
    if failed:
        out.append(f"\n**Grading failures (not scored, excluded):** {', '.join(failed)}")
    if missing:
        out.append(f"\n**Labeled calls without a usable grade:** {', '.join(missing)}")
    out.append(f"\n> n={len(labeled)} is small: one disagreement moves exact agreement by "
               f"{100 / max(len(labeled), 1):.0f} points. Read the per-call table, not just the rates.")

    # Per-criterion summary
    out += ["", "## Per criterion", "",
            "| Criterion | Exact | Within ±5 | Severe (0↔10) | Bias (grader − human) | Human dist. | Grader dist. | Weighted κ |",
            "|---|---|---|---|---|---|---|---|"]
    per_criterion = {}
    for cid, name in rubric.criteria.items():
        h = [labels[c][cid] for c in labeled]
        g = [grades[c]["grades"][cid]["score"] for c in labeled]
        n = len(h)
        if n == 0:
            continue
        exact = sum(a == b for a, b in zip(h, g))
        within = sum(abs(a - b) <= step for a, b in zip(h, g))
        severe = sum(abs(a - b) == worst for a, b in zip(h, g))
        bias = mean(g) - mean(h)
        dist = lambda xs: " / ".join(f"{s}:{xs.count(s)}" for s in scale)
        kappa = weighted_kappa(h, g, scale)
        dominant = Counter(h).most_common(1)[0][1] / n
        if kappa is None:
            k_str = "undefined"
        elif dominant >= KAPPA_DOMINANT_SHARE:
            k_str = f"{kappa:.2f} ⚠ unstable (human labels {dominant:.0%} one value)"
        else:
            k_str = f"{kappa:.2f}"
        out.append(f"| {cid} {name} | {pct(exact, n)} | {pct(within, n)} | {severe} | {bias:+.1f} | "
                   f"{dist(h)} | {dist(g)} | {k_str} |")
        per_criterion[cid] = (h, g)

    # Totals
    if labeled:
        ht = [sum(labels[c].values()) for c in labeled]
        gt = [grades[c]["total"] for c in labeled]
        out += ["", "## Total score (0–50)", "",
                f"- MAE: **{mean(abs(a - b) for a, b in zip(ht, gt)):.1f}** points",
                f"- Bias (grader − human): **{mean(gt) - mean(ht):+.1f}** points",
                f"- Exact total match: {pct(sum(a == b for a, b in zip(ht, gt)), len(ht))}"]

    # Tune / holdout split
    tune = [c for c in labeled if c in config.TUNE_IDS]
    hold = [c for c in labeled if c not in config.TUNE_IDS]
    out += ["", "## Tune vs holdout (exact agreement over all criteria)", "",
            "If the prompt was tuned by reading disagreements, only the tune calls were read; "
            "the holdout number is the one to trust."]
    for label, ids in (("tune", tune), ("holdout", hold)):
        cells = [(labels[c][k], grades[c]["grades"][k]["score"]) for c in ids for k in rubric.criteria]
        out.append(f"- {label} ({', '.join(ids) or 'none'}): {pct(sum(a == b for a, b in cells), len(cells))}")

    # Confusion matrices
    out += ["", "## Confusion matrices"]
    for cid, (h, g) in per_criterion.items():
        out += ["", f"**{cid} {rubric.criteria[cid]}**", ""] + confusion(h, g, scale)

    # Every disagreement, worst first
    rows = []
    for c in labeled:
        for cid in rubric.criteria:
            hs, gg = labels[c][cid], grades[c]["grades"][cid]
            if hs != gg["score"]:
                rows.append((abs(hs - gg["score"]), c, cid, hs, gg))
    rows.sort(key=lambda r: (-r[0], r[1], r[2]))
    out += ["", f"## Disagreements ({len(rows)})", "",
            "| Call | Crit | Human | Grader | Grader justification | Evidence | Quote found? |",
            "|---|---|---|---|---|---|---|"]
    for gap, c, cid, hs, gg in rows:
        flag = " **SEVERE**" if gap == worst else ""
        ev = (gg["evidence"] or "_(none: absence)_").replace("|", "\\|").replace("\n", " ")
        found = {True: "yes", False: "**NO**", None: "—"}[gg["evidence_found"]]
        out.append(f"| {c} | {cid}{flag} | {hs} | {gg['score']} | {gg['justification'].replace('|', '/')} | {ev} | {found} |")

    # Evidence integrity across all graded calls (labeled or not)
    ok = {c: g for c, g in grades.items() if g["status"] == "ok"}
    unverified = [(c, cid) for c, g in sorted(ok.items()) for cid, x in g["grades"].items() if x["evidence_found"] is False]
    out += ["", "## Evidence check (all graded calls)", "",
            f"Quotes that do not appear verbatim in the transcript: **{len(unverified)}**"
            + (": " + ", ".join(f"{c}/{cid}" for c, cid in unverified) if unverified else "")]

    # Distribution shift: does the grader behave differently on the unlabeled half?
    unlabeled = [c for c in sorted(ok) if c not in labels]
    if unlabeled and labeled:
        out += ["", "## Grader mean score: labeled vs unlabeled calls", "",
                "A large gap means the unlabeled calls differ from the calibration set, "
                "so calibration agreement may not carry over.", "",
                "| Criterion | C001–C015 | C016–C030 |", "|---|---|---|"]
        for cid in rubric.criteria:
            a = mean(ok[c]["grades"][cid]["score"] for c in labeled)
            b = mean(ok[c]["grades"][cid]["score"] for c in unlabeled)
            out.append(f"| {cid} | {a:.1f} | {b:.1f} |")

    return "\n".join(out) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    rubric = load_rubric()
    if not config.GRADES_PATH.exists():
        raise FileNotFoundError(f"{config.GRADES_PATH} not found. Run `python run.py` first.")
    grades = {g["call_id"]: g for g in json.loads(config.GRADES_PATH.read_text(encoding="utf-8"))}
    report = evaluate(grades, load_labels(rubric), rubric)
    config.EVAL_PATH.write_text(report, encoding="utf-8")
    print(report)
    print(f"(written to {config.EVAL_PATH})")


if __name__ == "__main__":
    main()
