"""JSON syntax and schema validation for extracted workshop records.

Syntax validation and schema validation are deliberately separate:

* **Syntax** asks "is this a valid JSON document at all?"
* **Schema** asks "does this JSON document satisfy the five-field contract?"

A document can pass syntax and fail schema. The application reports both
independently and never claims validity based only on successful parsing.
"""

from __future__ import annotations

import json
import re
from datetime import date
from typing import Any, Dict, List, Tuple

REQUIRED_FIELDS = ("title", "date", "venue", "speaker", "topics")
FIELD_TYPES = {
    "title": "string or null",
    "date": "ISO 8601 date string (YYYY-MM-DD) or null",
    "venue": "string or null",
    "speaker": "string or null",
    "topics": "array of strings",
}

NULL_SUBSTITUTES = {"null", "n/a", "na", "none", "unknown", "not available", "-", ""}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MAX_JSON_LENGTH = 20_000


def validate_json_text(raw: str) -> Tuple[bool, Any, List[str]]:
    """Parse *raw* as JSON. Return ``(ok, value, errors)``."""
    errors: List[str] = []
    if raw is None:
        return False, None, ["No JSON was supplied."]
    if not isinstance(raw, str):
        return False, None, ["JSON input must be a text string."]
    if not raw.strip():
        return False, None, ["The JSON input is empty."]
    if len(raw) > MAX_JSON_LENGTH:
        return False, None, [f"The JSON input exceeds the {MAX_JSON_LENGTH:,} character limit."]
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        errors.append(
            f"Invalid JSON syntax at line {exc.lineno}, column {exc.colno}: {exc.msg}."
        )
        return False, None, errors
    return True, value, errors


def _check_scalar(
    data: Dict[str, Any],
    field: str,
    errors: List[str],
    warnings: List[str],
) -> None:
    value = data[field]
    if value is None:
        return
    if not isinstance(value, str):
        errors.append(
            f"Field '{field}' must be a string or null, but received {type(value).__name__}."
        )
        return
    if value.strip() == "":
        errors.append(
            f"Field '{field}' must not be an empty string. Use JSON null for missing information."
        )
        return
    if value.strip().lower() in NULL_SUBSTITUTES:
        errors.append(
            f"Field '{field}' uses the string '{value}' instead of JSON null. "
            "Use null for missing information."
        )


def validate_date_value(value: Any) -> List[str]:
    """Validate a date field value. Return a list of error messages."""
    if value is None:
        return []
    if not isinstance(value, str):
        return [f"Field 'date' must be a string or null, but received {type(value).__name__}."]
    if value.strip() == "":
        return ["Field 'date' must not be an empty string. Use JSON null when no date is available."]
    if value.strip().lower() in NULL_SUBSTITUTES:
        return [f"Field 'date' uses the string '{value}' instead of JSON null."]
    if not DATE_RE.match(value):
        return [
            "Field 'date' must use ISO 8601 format YYYY-MM-DD, "
            f"but received '{value}'."
        ]
    try:
        date.fromisoformat(value)
    except ValueError:
        return [f"Field 'date' contains '{value}', which is not a real calendar date."]
    return []


def validate_schema(value: Any) -> Dict[str, Any]:
    """Validate *value* against the five-field schema.

    Returns a report with ``valid``, ``errors``, ``warnings``, ``checks`` and
    ``missing_fields`` / ``extra_fields``.
    """
    errors: List[str] = []
    warnings: List[str] = []
    checks: List[Dict[str, Any]] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    if not isinstance(value, dict):
        record("Root is a JSON object", False, f"Root value is {type(value).__name__}, not object.")
        return {
            "valid": False,
            "errors": ["The root JSON value must be an object with the five required fields."],
            "warnings": warnings,
            "checks": checks,
            "missing_fields": list(REQUIRED_FIELDS),
            "extra_fields": [],
        }
    record("Root is a JSON object", True, "The root value is a JSON object.")

    present = [field for field in REQUIRED_FIELDS if field in value]
    missing = [field for field in REQUIRED_FIELDS if field not in value]
    extra = [field for field in value if field not in REQUIRED_FIELDS]

    record(
        "All five required keys are present",
        not missing,
        "Present: " + ", ".join(present) if present else "No required keys are present.",
    )
    for field in missing:
        errors.append(f"Missing required field '{field}'.")

    record(
        "No extra keys are present",
        not extra,
        "No extra keys." if not extra else "Extra keys: " + ", ".join(sorted(extra)),
    )
    for field in extra:
        errors.append(f"Unexpected extra field '{field}'. Only the five schema fields are permitted.")

    if "title" in value:
        before = len(errors)
        _check_scalar(value, "title", errors, warnings)
        record(
            "title is a string or null",
            len(errors) == before,
            f"Received {type(value['title']).__name__}." if value["title"] is not None else "Received null.",
        )

    if "venue" in value:
        before = len(errors)
        _check_scalar(value, "venue", errors, warnings)
        record(
            "venue is a string or null",
            len(errors) == before,
            f"Received {type(value['venue']).__name__}." if value["venue"] is not None else "Received null.",
        )

    if "speaker" in value:
        before = len(errors)
        _check_scalar(value, "speaker", errors, warnings)
        record(
            "speaker is a string or null",
            len(errors) == before,
            f"Received {type(value['speaker']).__name__}." if value["speaker"] is not None else "Received null.",
        )

    if "date" in value:
        date_errors = validate_date_value(value["date"])
        errors.extend(date_errors)
        record(
            "date is a valid ISO date or null",
            not date_errors,
            date_errors[0] if date_errors else "Valid ISO 8601 date or null.",
        )

    if "topics" in value:
        topics = value["topics"]
        topic_errors: List[str] = []
        if not isinstance(topics, list):
            topic_errors.append(
                f"Field 'topics' must be an array of strings, but received {type(topics).__name__}."
            )
        else:
            for index, topic in enumerate(topics):
                if not isinstance(topic, str):
                    topic_errors.append(
                        f"Topic at index {index} must be a string, but received {type(topic).__name__}."
                    )
                elif not topic.strip():
                    topic_errors.append(f"Topic at index {index} is an empty string.")
        errors.extend(topic_errors)
        record(
            "topics is an array of non-empty strings",
            not topic_errors,
            topic_errors[0] if topic_errors else f"Array with {len(topics)} string topic(s).",
        )

    # Serialisability check: the report itself must be JSON-safe.
    serialisable = True
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError) as exc:
        serialisable = False
        errors.append(f"The output cannot be serialised back to valid JSON: {exc}")
    record(
        "Output can be serialised back to JSON",
        serialisable,
        "Serialisation succeeded." if serialisable else "Serialisation failed.",
    )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
        "missing_fields": missing,
        "extra_fields": sorted(extra),
    }


def validate_json_text_fully(raw: str) -> Dict[str, Any]:
    """Run syntax validation, then schema validation when syntax passes."""
    syntax_ok, value, syntax_errors = validate_json_text(raw)
    report: Dict[str, Any] = {
        "syntax": {"valid": syntax_ok, "errors": syntax_errors},
        "schema": {
            "valid": False,
            "errors": [],
            "warnings": [],
            "checks": [],
            "missing_fields": [],
            "extra_fields": [],
        },
        "valid": False,
    }
    if not syntax_ok:
        report["schema"]["errors"] = ["Schema validation was skipped because the JSON syntax is invalid."]
        return report

    schema = validate_schema(value)
    report["schema"] = schema
    report["valid"] = bool(syntax_ok and schema["valid"])
    report["parsed"] = value
    return report
