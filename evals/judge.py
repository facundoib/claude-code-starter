"""
LLM-as-judge for tasks where deterministic verifiers don't apply.

Per /engineering/multi-agent-research-system: a single call with a single
rubric and a single 0.0-1.0 score is the pattern that matched human raters
best. Multiple rubrics in one call introduce noise — if you need N rubrics,
run N calls.

Usage:
    from evals.judge import judge
    result = judge(rubric="The response should be empathetic and accurate.",
                   response="<the model output to grade>")
    # → {"score": 0.9, "reasoning": "..."}
"""

import json
import sys

import anthropic

JUDGE_MODEL = "claude-haiku-4-5-20251001"

JUDGE_PROMPT = """You are evaluating whether an AI assistant's response satisfies a specific requirement.

REQUIREMENT:
{rubric}

RESPONSE TO EVALUATE:
---
{response}
---

Score from 0.0 to 1.0 how well the response satisfies the requirement.
- 1.0 = fully satisfies the requirement, no caveats
- 0.7 = satisfies with minor issues
- 0.3 = partially satisfies, major issues remain
- 0.0 = does not satisfy at all

Output ONLY a JSON object with this exact format and no markdown fences:
{{"score": <float between 0.0 and 1.0>, "reasoning": "<one sentence explaining the score>"}}
"""


def judge(rubric: str, response: str) -> dict:
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": JUDGE_PROMPT.format(rubric=rubric, response=response),
        }],
    )
    text = "".join(b.text for b in msg.content if b.type == "text").strip()

    if text.startswith("```"):
        text = text.strip("`").lstrip("json").strip()

    return json.loads(text)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python evals/judge.py <rubric> <response>", file=sys.stderr)
        raise SystemExit(2)
    print(json.dumps(judge(sys.argv[1], sys.argv[2]), indent=2))
