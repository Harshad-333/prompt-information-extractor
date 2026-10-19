"""Tests for JSON syntax and schema validation."""

import json

import pytest

import samples
import validator


VALID = samples.TEST_SCENARIOS[0]["expected"]
MISSING = samples.TEST_SCENARIOS[1]["expected"]
SPARSE = samples.TEST_SCENARIOS[2]["expected"]


def test_valid_complete_record_passes():
    report = validator.validate_json_text_fully(json.dumps(VALID))
    assert report["syntax"]["valid"] is True
    assert report["schema"]["valid"] is True
    assert report["valid"] is True


def test_valid_missing_record_passes():
    report = validator.validate_json_text_fully(json.dumps(MISSING))
    assert report["valid"] is True


def test_valid_sparse_record_passes():
    report = validator.validate_json_text_fully(json.dumps(SPARSE))
    assert report["valid"] is True


# --------------------------------------------------------------------------
# Syntax
# --------------------------------------------------------------------------

def test_invalid_json_syntax_is_reported():
    report = validator.validate_json_text_fully('{"title": "x", }')
    assert report["syntax"]["valid"] is False
    assert report["valid"] is False
    assert report["syntax"]["errors"]
    assert "line" in report["syntax"]["errors"][0].lower()


def test_empty_json_is_invalid():
    report = validator.validate_json_text_fully("   ")
    assert report["syntax"]["valid"] is False
    assert report["valid"] is False


def test_syntax_and_schema_are_separate():
    # Valid JSON, but not an object -> syntax passes, schema fails.
    report = validator.validate_json_text_fully('["not", "an", "object"]')
    assert report["syntax"]["valid"] is True
    assert report["schema"]["valid"] is False
    assert report["valid"] is False


def test_root_must_be_object():
    report = validator.validate_schema("a string")
    assert report["valid"] is False
    assert any("object" in error.lower() for error in report["errors"])


# --------------------------------------------------------------------------
# Required and extra keys
# --------------------------------------------------------------------------

def test_missing_required_key_is_detected():
    data = dict(VALID)
    del data["speaker"]
    report = validator.validate_schema(data)
    assert report["valid"] is False
    assert "speaker" in report["missing_fields"]
    assert any("speaker" in error for error in report["errors"])


def test_extra_key_is_detected():
    data = dict(VALID)
    data["extra"] = "not allowed"
    report = validator.validate_schema(data)
    assert report["valid"] is False
    assert "extra" in report["extra_fields"]
    assert any("extra" in error.lower() for error in report["errors"])


@pytest.mark.parametrize("key", ["title", "date", "venue", "speaker", "topics"])
def test_each_required_key_is_enforced(key):
    data = dict(VALID)
    del data[key]
    report = validator.validate_schema(data)
    assert report["valid"] is False
    assert key in report["missing_fields"]


# --------------------------------------------------------------------------
# Types
# --------------------------------------------------------------------------

def test_wrong_scalar_type_is_detected():
    data = dict(VALID)
    data["title"] = 123
    report = validator.validate_schema(data)
    assert report["valid"] is False
    assert any("title" in error for error in report["errors"])


def test_topics_must_be_array():
    data = dict(VALID)
    data["topics"] = "Prompt Design"
    report = validator.validate_schema(data)
    assert report["valid"] is False
    assert any("topics" in error for error in report["errors"])


def test_topics_must_contain_only_strings():
    data = dict(VALID)
    data["topics"] = ["Prompt Design", 42]
    report = validator.validate_schema(data)
    assert report["valid"] is False
    assert any("index 1" in error for error in report["errors"])


def test_topics_rejects_empty_string():
    data = dict(VALID)
    data["topics"] = ["Prompt Design", ""]
    report = validator.validate_schema(data)
    assert report["valid"] is False


def test_empty_string_scalar_is_rejected():
    for field in ("title", "venue", "speaker"):
        data = dict(VALID)
        data[field] = ""
        report = validator.validate_schema(data)
        assert report["valid"] is False, field


@pytest.mark.parametrize("substitute", ["null", "N/A", "Unknown", "None", "-"])
def test_null_substitute_strings_are_rejected(substitute):
    data = dict(VALID)
    data["venue"] = substitute
    report = validator.validate_schema(data)
    assert report["valid"] is False
    assert any("null" in error.lower() for error in report["errors"])


def test_actual_json_null_is_accepted():
    data = dict(VALID)
    data["venue"] = None
    report = validator.validate_schema(data)
    assert report["valid"] is True


# --------------------------------------------------------------------------
# Dates
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "value",
    ["15-11-2026", "2026/11/15", "2026-13-01", "2026-02-30", "15 November 2026", "2026-1-5"],
)
def test_invalid_date_formats_are_rejected(value):
    data = dict(VALID)
    data["date"] = value
    report = validator.validate_schema(data)
    assert report["valid"] is False
    assert any("date" in error for error in report["errors"])


def test_null_date_is_accepted():
    data = dict(VALID)
    data["date"] = None
    report = validator.validate_schema(data)
    assert report["valid"] is True


def test_leap_day_is_accepted():
    data = dict(VALID)
    data["date"] = "2028-02-29"
    report = validator.validate_schema(data)
    assert report["valid"] is True


# --------------------------------------------------------------------------
# Checks and serialisation
# --------------------------------------------------------------------------

def test_checks_are_reported_individually():
    report = validator.validate_schema(VALID)
    names = [check["name"] for check in report["checks"]]
    assert "Root is a JSON object" in names
    assert "All five required keys are present" in names
    assert "No extra keys are present" in names
    assert "date is a valid ISO date or null" in names
    assert "topics is an array of non-empty strings" in names
    assert "Output can be serialised back to JSON" in names
    assert all(check["passed"] for check in report["checks"])


def test_report_is_json_serialisable():
    report = validator.validate_schema(VALID)
    assert json.loads(json.dumps(report)) == report


def test_oversized_json_is_rejected():
    report = validator.validate_json_text_fully('{"title": "' + "a" * 25000 + '"}')
    assert report["syntax"]["valid"] is False
    assert any("limit" in error.lower() for error in report["syntax"]["errors"])
