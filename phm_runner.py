# phm_runner.py
import json
from agents.prompt_agent import run_prompt
from agents.error_agent import analyze_response
from agents.repair_agent import attempt_repair_and_rerun
from db.db_utils import insert_log
from utils.logger import logger

def load_tests(path="tests/test_cases.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_prompt_from_test(test):
    # simple template replacement for {{invoice_text}}
    prompt = test["prompt_template"]
    if "{{invoice_text}}" in prompt:
        prompt = prompt.replace("{{invoice_text}}", test["input_example_json"]["invoice_text"])
    return prompt

def run_test(test_id: str, engine: str = "mock", dry_run_repair: bool = True):
    tests = load_tests()
    test = next((t for t in tests if t["id"] == test_id), None)
    if not test:
        raise ValueError(f"Test {test_id} not found")
    prompt = build_prompt_from_test(test)
    out = run_prompt(prompt, engine=engine)
    analysis = analyze_response(out, expected_schema=test.get("expected_output_json", {}).get("json_schema"))
    insert_log("phm_runner", prompt, out, error_type=analysis.get("error_type"), fix_suggestion=analysis.get("suggestion"))
    result = {"test_id": test_id, "engine": engine, "output": out, "analysis": analysis}

    if analysis.get("error_type") is not None:
        # try repair (dry run by default)
        repair_results = attempt_repair_and_rerun(prompt,
                                                 schema=test.get("expected_output_json", {}).get("json_schema"),
                                                 example_input=test["input_example_json"]["invoice_text"],
                                                 example_example_output=test.get("expected_output_json", {}).get("canonical_example"),
                                                 engine=engine,
                                                 dry_run=dry_run_repair)
        result["repair_candidates"] = repair_results

    return result

if __name__ == "__main__":
    import sys
    tid = sys.argv[1] if len(sys.argv) > 1 else "invoice_json_v1"
    print(run_test(tid, engine="mock", dry_run_repair=True))
