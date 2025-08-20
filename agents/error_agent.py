# agents/error_agent.py
import json
from jsonschema import validate, ValidationError
from utils.logger import logger

def analyze_response(output_text: str, expected_schema: dict = None) -> dict:
    """
    Returns analysis dict:
      { error_type: None|'invalid_json'|'schema_mismatch', suggestion: str, parsed: dict|None }
    """
    try:
        parsed = json.loads(output_text)
    except Exception:
        suggestion = (
            "Response is not valid JSON. Suggestion: append to your prompt:\n"
            "\"Output ONLY valid JSON matching the schema: <schema>. If value missing, use null.\""
        )
        logger.info("analyze_response: invalid_json")
        return {"error_type": "invalid_json", "suggestion": suggestion, "parsed": None}

    if expected_schema:
        try:
            validate(instance=parsed, schema=expected_schema)
            logger.info("analyze_response: schema valid")
            return {"error_type": None, "suggestion": None, "parsed": parsed}
        except ValidationError as e:
            suggestion = (
                f"JSON parsed but failed schema validation: {e.message}. "
                "Suggestion: Add stricter instruction: Output only JSON matching the schema; use null for missing fields."
            )
            logger.info("analyze_response: schema_mismatch: %s", e.message)
            return {"error_type": "schema_mismatch", "suggestion": suggestion, "parsed": parsed}

    # parsed and no schema -> OK
    logger.info("analyze_response: parsed_ok_no_schema")
    return {"error_type": None, "suggestion": None, "parsed": parsed}
