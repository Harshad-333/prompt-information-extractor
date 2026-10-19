"""Tests for the deterministic extraction engine."""

import json

import pytest

import extractor
import samples


COMPLETE = samples.SAMPLE_BY_ID["complete"]["text"]
MISSING = samples.SAMPLE_BY_ID["missing"]["text"]
SPARSE = samples.SAMPLE_BY_ID["sparse"]["text"]
NO_DETAILS = samples.SAMPLE_BY_ID["empty"]["text"]


# --------------------------------------------------------------------------
# Required scenarios
# --------------------------------------------------------------------------

def test_complete_paragraph_all_fields():
    data = extractor.extract_data(COMPLETE)
    assert data == samples.TEST_SCENARIOS[0]["expected"]


def test_complete_paragraph_venue_includes_institute_and_city():
    data = extractor.extract_data(COMPLETE)
    assert data["venue"].startswith("Seminar Hall")
    assert "Ichalkaranji" in data["venue"]


def test_complete_paragraph_date_is_iso():
    data = extractor.extract_data(COMPLETE)
    assert data["date"] == "2026-11-15"


def test_missing_venue_and_speaker_are_null():
    data = extractor.extract_data(MISSING)
    assert data["venue"] is None
    assert data["speaker"] is None
    assert data["title"] == "Python programming workshop"
    assert data["date"] == "2026-12-20"
    assert data["topics"] == ["file handling", "exception handling"]


def test_sparse_paragraph_is_fully_null():
    data = extractor.extract_data(SPARSE, mode="safe")
    assert data == {
        "title": None,
        "date": None,
        "venue": None,
        "speaker": None,
        "topics": [],
    }


def test_sparse_paragraph_standard_mode_also_null():
    data = extractor.extract_data(SPARSE, mode="standard")
    assert data["title"] is None
    assert data["date"] is None
    assert data["speaker"] is None


def test_no_workshop_details_paragraph():
    data = extractor.extract_data(NO_DETAILS)
    assert data["title"] is None
    assert data["date"] is None
    assert data["venue"] is None
    assert data["speaker"] is None
    assert data["topics"] == []


# --------------------------------------------------------------------------
# Empty and malformed input
# --------------------------------------------------------------------------

@pytest.mark.parametrize("value", ["", "   ", "\n\n\t"])
def test_empty_paragraph_returns_schema(value):
    data = extractor.extract_data(value)
    assert set(data) == {"title", "date", "venue", "speaker", "topics"}
    assert data["title"] is None
    assert data["date"] is None
    assert data["venue"] is None
    assert data["speaker"] is None
    assert data["topics"] == []


def test_invalid_mode_raises():
    with pytest.raises(ValueError):
        extractor.extract(COMPLETE, mode="unknown")


# --------------------------------------------------------------------------
# Dates
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "text,expected",
    [
        ("The workshop is on 15 November 2026.", "2026-11-15"),
        ("The workshop is on November 15, 2026.", "2026-11-15"),
        ("The workshop is on 1st January 2027.", "2027-01-01"),
        ("The workshop is on 2026-11-15.", "2026-11-15"),
        ("The workshop is on 29 February 2028.", "2028-02-29"),
    ],
)
def test_valid_date_formats(text, expected):
    value, _, note = extractor.extract_date(text)
    assert value == expected
    assert note is None


@pytest.mark.parametrize(
    "text",
    [
        "The workshop is on 31 February 2026.",
        "The workshop is on 15 November.",
        "The workshop is next month.",
        "The workshop is tomorrow.",
        "The workshop is on 03/04/2026.",
    ],
)
def test_ambiguous_or_invalid_dates_are_null(text):
    value, _, note = extractor.extract_date(text)
    assert value is None
    assert note


def test_date_evidence_recorded():
    result = extractor.extract(COMPLETE)
    assert "15 November 2026" in result["meta"]["evidence"]["date"]


# --------------------------------------------------------------------------
# Title
# --------------------------------------------------------------------------

def test_title_normalised_for_missing_paragraph():
    data = extractor.extract_data(MISSING)
    assert data["title"] == "Python programming workshop"


def test_generic_title_rejected_in_safe_mode():
    data = extractor.extract_data("An international conference will be held on 5 May 2027.", mode="safe")
    assert data["title"] is None


def test_generic_title_fallback_in_standard_mode_requires_specificity():
    # Four content words, no proper noun -> allowed by the documented standard rule.
    data = extractor.extract_data(
        "A national workshop on data science will be organized on 5 May 2027.",
        mode="standard",
    )
    assert data["title"] is not None
    assert "data science" in data["title"]


def test_title_not_expanded_with_unsupported_details():
    data = extractor.extract_data(MISSING)
    assert "DKTE" not in (data["title"] or "")
    assert data["title"] == "Python programming workshop"


# --------------------------------------------------------------------------
# Speaker
# --------------------------------------------------------------------------

def test_speaker_extracted_with_honorific():
    data = extractor.extract_data(COMPLETE)
    assert data["speaker"] == "Dr. Ananya Deshmukh"


def test_role_only_speaker_is_null():
    text = "A workshop on Python will be held on 5 May 2027. The speaker will be a senior faculty member."
    data = extractor.extract_data(text)
    assert data["speaker"] is None


def test_unannounced_speaker_is_null():
    data = extractor.extract_data("The speaker has not been announced. A workshop is planned.")
    assert data["speaker"] is None


# --------------------------------------------------------------------------
# Topics
# --------------------------------------------------------------------------

def test_topics_split_on_commas_and_and():
    data = extractor.extract_data(COMPLETE)
    assert data["topics"] == [
        "Prompt Design",
        "Structured JSON Output",
        "Context Engineering",
        "AI Output Validation",
    ]


def test_topics_are_deduplicated():
    text = "A workshop will be held. It will cover Python, python, and SQL."
    data = extractor.extract_data(text)
    assert data["topics"] == ["Python", "SQL"]


def test_no_topic_cue_gives_empty_array():
    data = extractor.extract_data("A workshop will be held on 5 May 2027 in the Auditorium.")
    assert data["topics"] == []


# --------------------------------------------------------------------------
# Contract and metadata
# --------------------------------------------------------------------------

def test_output_always_has_exactly_five_keys():
    for paragraph in (COMPLETE, MISSING, SPARSE, NO_DETAILS, ""):
        data = extractor.extract_data(paragraph)
        assert list(data.keys()) == ["title", "date", "venue", "speaker", "topics"]


def test_output_is_json_serialisable():
    data = extractor.extract_data(COMPLETE)
    assert json.loads(json.dumps(data)) == data


def test_meta_reports_engine_honestly():
    result = extractor.extract(COMPLETE)
    assert result["meta"]["engine"] == "deterministic-rule-based"
    assert result["meta"]["mode"] == "standard"


def test_notes_explain_missing_fields():
    result = extractor.extract(MISSING)
    joined = " ".join(result["meta"]["notes"]).lower()
    assert "venue" in joined
    assert "speaker" in joined


def test_labelled_input_is_supported():
    text = (
        "Title: Cloud Computing Workshop\n"
        "Date: 3 March 2027\n"
        "Venue: Computer Lab\n"
        "Speaker: Prof. R. S. Patil\n"
        "Topics: Docker, Kubernetes\n"
    )
    data = extractor.extract_data(text)
    assert data["title"] == "Cloud Computing Workshop"
    assert data["date"] == "2027-03-03"
    assert data["venue"] == "Computer Lab"
    assert data["speaker"] == "Prof. R. S. Patil"
    assert data["topics"] == ["Docker", "Kubernetes"]


def test_long_paragraph_does_not_crash():
    data = extractor.extract_data("A workshop. " * 2000)
    assert set(data) == {"title", "date", "venue", "speaker", "topics"}
