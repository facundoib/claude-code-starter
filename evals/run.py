"""
Lightweight eval harness runner.

Usage:
    pip install -r evals/requirements.txt
    export ANTHROPIC_API_KEY=...
    python evals/run.py

Source patterns:
    /engineering/demystifying-evals-for-ai-agents (start small, run before every change)
    /engineering/multi-agent-research-system     (single rubric LLM judge, end-state grading)
    /engineering/infrastructure-noise            (multiple trials, report variance)
"""

import json
import os
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic

from judge import judge

MODEL = os.environ.get("EVAL_MODEL", "claude-sonnet-4-6")
TRIALS_PER_TASK = int(os.environ.get("EVAL_TRIALS", "3"))
MAX_TOKENS = 1024
REGRESSION_THRESHOLD = 0.05  # 5pp drop counts as regression
DEFAULT_JUDGE_THRESHOLD = 0.7

REPO_ROOT = Path(__file__).resolve().parent.parent
EVALS_DIR = REPO_ROOT / "evals"
TASKS_FILE = EVALS_DIR / "tasks.jsonl"
RESULTS_DIR = EVALS_DIR / "results"
BASELINE_FILE = EVALS_DIR / "last_results.json"


def load_tasks():
    return [json.loads(line) for line in TASKS_FILE.read_text().splitlines() if line.strip()]


def call_model(client, prompt, system=None):
    kwargs = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system

    t0 = time.time()
    resp = client.messages.create(**kwargs)
    elapsed = time.time() - t0

    text = "".join(b.text for b in resp.content if b.type == "text")
    return {
        "text": text,
        "tokens_in": resp.usage.input_tokens,
        "tokens_out": resp.usage.output_tokens,
        "wall_s": elapsed,
    }


def verify(task, output_text):
    """Return True/False/None. None means deferred to LLM judge."""
    vtype = task["verifier"]
    args = task.get("args", {})

    if vtype == "exact_match":
        return output_text.strip().lower() == args["expected"].strip().lower()

    if vtype == "regex_match":
        return bool(re.search(args["pattern"], output_text, re.MULTILINE))

    if vtype == "contains_all":
        return all(s.lower() in output_text.lower() for s in args["needles"])

    if vtype == "contains_none":
        return not any(s.lower() in output_text.lower() for s in args["needles"])

    if vtype == "llm_judge":
        return None  # deferred to LLM-judge in run_task

    raise ValueError(f"Unknown verifier: {vtype}")


def run_task(client, task):
    trials = []
    for _ in range(TRIALS_PER_TASK):
        try:
            out = call_model(client, task["prompt"], task.get("system"))
            passed = verify(task, out["text"])
            judge_score = None
            if passed is None and task["verifier"] == "llm_judge":
                jr = judge(rubric=task["args"]["rubric"], response=out["text"])
                judge_score = jr.get("score")
                threshold = task["args"].get("threshold", DEFAULT_JUDGE_THRESHOLD)
                passed = judge_score is not None and judge_score >= threshold
        except anthropic.APIError as e:
            trials.append({"passed": False, "error": str(e), "tokens_in": 0, "tokens_out": 0, "wall_s": 0})
            continue

        trial = {
            "passed": passed,
            "tokens_in": out["tokens_in"],
            "tokens_out": out["tokens_out"],
            "wall_s": out["wall_s"],
            "output_preview": out["text"][:300],
        }
        if judge_score is not None:
            trial["judge_score"] = judge_score
        trials.append(trial)

    pass_results = [t["passed"] for t in trials if t.get("passed") is not None]
    pass_rate = sum(pass_results) / len(pass_results) if pass_results else None

    return {
        "id": task["id"],
        "summary": task.get("summary", ""),
        "trials": trials,
        "pass_rate": pass_rate,
        "mean_tokens_in": statistics.mean(t["tokens_in"] for t in trials) if trials else 0,
        "mean_tokens_out": statistics.mean(t["tokens_out"] for t in trials) if trials else 0,
        "mean_wall_s": statistics.mean(t["wall_s"] for t in trials) if trials else 0,
    }


def diff_against_baseline(results):
    if not BASELINE_FILE.exists():
        return None

    baseline = json.loads(BASELINE_FILE.read_text())
    baseline_by_id = {r["id"]: r for r in baseline.get("results", [])}

    regressions, improvements = [], []
    for r in results:
        b = baseline_by_id.get(r["id"])
        if not b or r["pass_rate"] is None or b.get("pass_rate") is None:
            continue
        delta = r["pass_rate"] - b["pass_rate"]
        if delta < -REGRESSION_THRESHOLD:
            regressions.append((r["id"], b["pass_rate"], r["pass_rate"]))
        elif delta > REGRESSION_THRESHOLD:
            improvements.append((r["id"], b["pass_rate"], r["pass_rate"]))

    return regressions, improvements


def print_report(results, out_path, diff):
    pass_rates = [r["pass_rate"] for r in results if r["pass_rate"] is not None]
    overall = sum(pass_rates) / len(pass_rates) if pass_rates else 0
    total_in = sum(r["mean_tokens_in"] for r in results) * TRIALS_PER_TASK
    total_out = sum(r["mean_tokens_out"] for r in results) * TRIALS_PER_TASK
    total_wall = sum(r["mean_wall_s"] for r in results) * TRIALS_PER_TASK

    print()
    print("=" * 60)
    print(f"Model:           {MODEL}")
    print(f"Tasks:           {len(results)}")
    print(f"Trials per task: {TRIALS_PER_TASK}")
    print(f"Pass rate:       {overall:.1%}")
    print(f"Tokens in/out:   {total_in:.0f} / {total_out:.0f}")
    print(f"Wall time:       {total_wall:.1f}s")
    print(f"Saved to:        {out_path.relative_to(REPO_ROOT)}")
    print("=" * 60)

    failed = [r for r in results if r["pass_rate"] is not None and r["pass_rate"] < 1.0]
    if failed:
        print(f"\nTasks with at least one failed trial:")
        for r in failed:
            print(f"  {r['id']} ({r['pass_rate']:.0%}): {r['summary']}")

    if diff is None:
        print(f"\nNo baseline yet. To set this run as baseline:")
        print(f"  cp {out_path.relative_to(REPO_ROOT)} {BASELINE_FILE.relative_to(REPO_ROOT)}")
        return

    regressions, improvements = diff
    if not regressions and not improvements:
        print(f"\nNo significant changes vs baseline (threshold ±{REGRESSION_THRESHOLD:.0%}).")
        return

    if regressions:
        print(f"\nREGRESSIONS ({len(regressions)}) — DO NOT update baseline:")
        for tid, old, new in regressions:
            print(f"  {tid}: {old:.0%} → {new:.0%}")
    if improvements:
        print(f"\nImprovements ({len(improvements)}):")
        for tid, old, new in improvements:
            print(f"  {tid}: {old:.0%} → {new:.0%}")

    if improvements and not regressions:
        print(f"\nSafe to update baseline:")
        print(f"  cp {out_path.relative_to(REPO_ROOT)} {BASELINE_FILE.relative_to(REPO_ROOT)}")


def main():
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("ERROR: ANTHROPIC_API_KEY not set in environment.", file=sys.stderr)
        return 2

    client = anthropic.Anthropic()
    tasks = load_tasks()
    print(f"Running {len(tasks)} tasks × {TRIALS_PER_TASK} trials = {len(tasks) * TRIALS_PER_TASK} calls...")

    results = []
    for i, task in enumerate(tasks, 1):
        summary = task.get("summary", task["prompt"][:50])
        print(f"  [{i:2}/{len(tasks)}] {task['id']}: {summary}")
        results.append(run_task(client, task))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / f"{timestamp}.json"

    summary_doc = {
        "timestamp": timestamp,
        "model": MODEL,
        "trials_per_task": TRIALS_PER_TASK,
        "results": results,
    }
    out_path.write_text(json.dumps(summary_doc, indent=2))

    diff = diff_against_baseline(results)
    print_report(results, out_path, diff)

    if diff and diff[0]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
