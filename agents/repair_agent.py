# agents/repair_agent.py
import json
from typing import Dict, Any
from agents.prompt_agent import run_prompt
from agents.error_agent import analyze_response
from utils.logger import logger

def enforce_format_prompt(base_prompt: str, schema: Dict[str, Any]) -> str:
    """
    Append strict JSON output instruction and inline schema.
    """
    instr = (
        "\n\nIMPORTANT: Output ONLY valid JSON and nothing else. "
        "Match the following JSON schema exactly. If a field cannot be extracted, set it to null.\n\n"
        f"SCHEMA:\n{json.dumps(schema, indent=2)}\n"
    )
    return base_prompt + instr

def few_shot_prompt(base_prompt: str, example_input: str, example_output: Dict[str, Any]) -> str:
    ex = json.dumps(example_output, sort_keys=True)
    fs = f"EXAMPLE INPUT:\n{example_input}\nEXAMPLE OUTPUT:\n{ex}\n\nNow, for the real input: {base_prompt}"
    return fs

def attempt_repair_and_rerun(base_prompt: str, schema: Dict[str, Any], example_input: str, example_example_output: Dict[str, Any],
                             engine: str = "mock", dry_run: bool = True):
    """
    Returns list of candidate results. Each item is dict:
      { strategy, prompt, output (if run), analysis (if run) }
    """
    candidates = []

    # 1) format enforcement (least aggressive)
    p1 = enforce_format_prompt(base_prompt, schema) if schema else base_prompt
    candidates.append(("format_enforcement", p1))

    # 2) few-shot injection
    p2 = few_shot_prompt(base_prompt, example_input, example_example_output)
    candidates.append(("few_shot", p2))

    results = []
    for strategy, cand in candidates:
        if dry_run:
            results.append({"strategy": strategy, "prompt": cand, "output": None, "analysis": None})
            continue
        # run candidate
        out = run_prompt(cand, engine=engine)
        analysis = analyze_response(out, expected_schema=schema)
        results.append({"strategy": strategy, "prompt": cand, "output": out, "analysis": analysis})
        if analysis.get("error_type") is None:
            logger.info("attempt_repair: candidate succeeded strategy=%s", strategy)
            break
    return results
