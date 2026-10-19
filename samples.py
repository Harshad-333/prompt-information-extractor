"""Illustrative sample paragraphs and the three required test scenarios.

All sample data is fictional and exists only for this practical examination.
It does not describe a verified real-world event.
"""

from __future__ import annotations

from typing import Any, Dict, List

SAMPLE_PARAGRAPHS: List[Dict[str, str]] = [
    {
        "id": "complete",
        "label": "Complete workshop",
        "description": "All five fields are stated explicitly. Illustrative sample data.",
        "text": (
            "DKTE Society's Textile & Engineering Institute, Ichalkaranji, will organize "
            "the Introduction to Generative AI and Prompt Engineering Workshop on "
            "15 November 2026 in the Seminar Hall. Dr. Ananya Deshmukh will be the speaker. "
            "The workshop will cover Prompt Design, Structured JSON Output, Context Engineering, "
            "and AI Output Validation."
        ),
    },
    {
        "id": "missing",
        "label": "Missing venue and speaker",
        "description": "The date, title, and topics are present; venue and speaker are absent.",
        "text": (
            "The college will conduct a Python programming workshop on 20 December 2026. "
            "Students will learn file handling and exception handling."
        ),
    },
    {
        "id": "sparse",
        "label": "Sparse / ambiguous",
        "description": "Relative date, generic event description, and an unannounced speaker.",
        "text": (
            "A technical workshop will be organized next month. "
            "The speaker has not been announced."
        ),
    },
    {
        "id": "empty",
        "label": "No workshop details",
        "description": "A paragraph with no event information at all; every field must stay empty.",
        "text": (
            "The library will remain open until 8 PM during the examination week. "
            "Students should carry their identity cards."
        ),
    },
]

SAMPLE_BY_ID = {item["id"]: item for item in SAMPLE_PARAGRAPHS}

TEST_SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "test-1",
        "name": "TEST 1 - Complete Information",
        "mode": "standard",
        "description": "All five fields are explicitly stated in the paragraph.",
        "input": SAMPLE_BY_ID["complete"]["text"],
        "expected": {
            "title": "Introduction to Generative AI and Prompt Engineering Workshop",
            "date": "2026-11-15",
            "venue": (
                "Seminar Hall, DKTE Society's Textile & Engineering Institute, Ichalkaranji"
            ),
            "speaker": "Dr. Ananya Deshmukh",
            "topics": [
                "Prompt Design",
                "Structured JSON Output",
                "Context Engineering",
                "AI Output Validation",
            ],
        },
        "explanation": (
            "Every field is supported by an explicit phrase in the paragraph, so no "
            "missing-information rule is triggered."
        ),
    },
    {
        "id": "test-2",
        "name": "TEST 2 - Missing Information",
        "mode": "standard",
        "description": "Venue and speaker are not stated and must be null.",
        "input": SAMPLE_BY_ID["missing"]["text"],
        "expected": {
            "title": "Python programming workshop",
            "date": "2026-12-20",
            "venue": None,
            "speaker": None,
            "topics": ["file handling", "exception handling"],
        },
        "explanation": (
            "The paragraph names no venue and no speaker, so both fields are JSON null. "
            "The title is normalized to 'Python programming workshop' by the documented "
            "title rule and is not expanded with unsupported details."
        ),
    },
    {
        "id": "test-3",
        "name": "TEST 3 - Sparse / Ambiguous Information",
        "mode": "safe",
        "description": "Relative date, generic title, and unannounced speaker.",
        "input": SAMPLE_BY_ID["sparse"]["text"],
        "expected": {
            "title": None,
            "date": None,
            "venue": None,
            "speaker": None,
            "topics": [],
        },
        "explanation": (
            "'Next month' is not an unambiguous calendar date, 'technical workshop' is a "
            "generic description rather than a specific title, and the speaker is explicitly "
            "not announced. All values are therefore null / empty."
        ),
    },
]

EXPECTED_SAMPLE_OUTPUT = TEST_SCENARIOS[0]["expected"]
EXPECTED_MISSING_OUTPUT = TEST_SCENARIOS[1]["expected"]

DISCLAIMER = (
    "The workshop paragraph, speaker name, and test data are illustrative sample data "
    "created for this MCA practical examination. They do not describe a verified "
    "real-world event."
)


def compare_fields(actual: Dict[str, Any], expected: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return a field-by-field comparison used by the test runner and the UI."""
    fields = ["title", "date", "venue", "speaker", "topics"]
    results: List[Dict[str, Any]] = []
    for field in fields:
        actual_value = actual.get(field, "<missing>")
        expected_value = expected.get(field, "<missing>")
        results.append(
            {
                "field": field,
                "expected": expected_value,
                "actual": actual_value,
                "passed": actual_value == expected_value,
            }
        )
    return results
