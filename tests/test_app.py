"""Tests for the Flask endpoints and pages."""

import json

import pytest

import samples
from app import create_app


@pytest.fixture()
def client():
    app = create_app({"TESTING": True})
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def app_instance():
    return create_app({"TESTING": True})


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------

def test_index_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Prompt-Based Information Extraction System" in body
    assert "Harshad Babulal Imale" in body
    assert "Extract Information" in body


def test_report_page_renders(client):
    response = client.get("/report")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Experiment Report" in body
    assert "Viva Questions" in body


def test_unknown_page_returns_404_page(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert "Page not found" in response.get_data(as_text=True)


# --------------------------------------------------------------------------
# Health and metadata
# --------------------------------------------------------------------------

def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["status"] == "healthy"
    assert payload["engine"] == "deterministic-rule-based"
    assert payload["external_api_required"] is False


def test_samples_endpoint(client):
    response = client.get("/api/samples")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert len(payload["samples"]) >= 4
    assert len(payload["tests"]) == 3


def test_prompts_endpoint(client):
    response = client.get("/api/prompts")
    assert response.status_code == 200
    payload = response.get_json()
    assert set(payload["prompts"]) == {"standard", "safe"}
    assert "OUTPUT SCHEMA" in payload["prompts"]["standard"]["template"]


# --------------------------------------------------------------------------
# /api/extract
# --------------------------------------------------------------------------

def test_extract_complete_paragraph(client):
    response = client.post(
        "/api/extract",
        json={"paragraph": samples.SAMPLE_BY_ID["complete"]["text"], "mode": "standard"},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["data"] == samples.TEST_SCENARIOS[0]["expected"]
    assert payload["validation"]["syntax"]["valid"] is True
    assert payload["validation"]["schema"]["valid"] is True
    assert payload["validation"]["valid"] is True
    assert payload["prompt"]


def test_extract_missing_information(client):
    response = client.post(
        "/api/extract",
        json={"paragraph": samples.SAMPLE_BY_ID["missing"]["text"], "mode": "standard"},
    )
    payload = response.get_json()
    assert response.status_code == 200
    assert payload["data"]["venue"] is None
    assert payload["data"]["speaker"] is None


def test_extract_sparse_safe_mode(client):
    response = client.post(
        "/api/extract",
        json={"paragraph": samples.SAMPLE_BY_ID["sparse"]["text"], "mode": "safe"},
    )
    payload = response.get_json()
    assert response.status_code == 200
    assert payload["data"] == samples.TEST_SCENARIOS[2]["expected"]


def test_extract_defaults_to_standard_mode(client):
    response = client.post("/api/extract", json={"paragraph": "A workshop on 5 May 2027."})
    assert response.status_code == 200
    assert response.get_json()["meta"]["mode"] == "standard"


def test_extract_empty_paragraph_returns_400(client):
    response = client.post("/api/extract", json={"paragraph": "   ", "mode": "standard"})
    assert response.status_code == 400
    assert response.get_json()["ok"] is False


def test_extract_missing_paragraph_field_returns_400(client):
    response = client.post("/api/extract", json={"mode": "standard"})
    assert response.status_code == 400
    assert "empty" in response.get_json()["error"].lower()


def test_extract_unsupported_mode_returns_400(client):
    response = client.post(
        "/api/extract", json={"paragraph": "A workshop.", "mode": "creative"}
    )
    assert response.status_code == 400
    assert "mode" in response.get_json()["error"].lower()


def test_extract_non_string_paragraph_returns_400(client):
    response = client.post("/api/extract", json={"paragraph": 123, "mode": "standard"})
    assert response.status_code == 400


def test_extract_requires_json_content_type(client):
    response = client.post("/api/extract", data="paragraph=hello", content_type="text/plain")
    assert response.status_code == 415


def test_extract_malformed_json_returns_400(client):
    response = client.post(
        "/api/extract", data="{not json", content_type="application/json"
    )
    assert response.status_code == 400
    assert response.get_json()["ok"] is False


def test_extract_json_array_body_returns_400(client):
    response = client.post("/api/extract", json=["a", "b"])
    assert response.status_code == 400


def test_extract_over_length_returns_400(client):
    response = client.post(
        "/api/extract", json={"paragraph": "a" * 5001, "mode": "standard"}
    )
    assert response.status_code == 400
    assert "limit" in response.get_json()["error"].lower()


# --------------------------------------------------------------------------
# /api/validate
# --------------------------------------------------------------------------

def test_validate_valid_json_string(client):
    response = client.post(
        "/api/validate", json={"json": json.dumps(samples.TEST_SCENARIOS[0]["expected"])}
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["syntax"]["valid"] is True
    assert payload["schema"]["valid"] is True
    assert payload["valid"] is True


def test_validate_accepts_object(client):
    response = client.post("/api/validate", json={"json": samples.TEST_SCENARIOS[1]["expected"]})
    assert response.status_code == 200
    assert response.get_json()["valid"] is True


def test_validate_invalid_json(client):
    response = client.post("/api/validate", json={"json": '{"title": }'})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["syntax"]["valid"] is False
    assert payload["valid"] is False


def test_validate_missing_key(client):
    data = dict(samples.TEST_SCENARIOS[0]["expected"])
    del data["venue"]
    response = client.post("/api/validate", json={"json": data})
    payload = response.get_json()
    assert payload["schema"]["valid"] is False
    assert "venue" in payload["schema"]["missing_fields"]


def test_validate_extra_key(client):
    data = dict(samples.TEST_SCENARIOS[0]["expected"])
    data["notes"] = "extra"
    response = client.post("/api/validate", json={"json": data})
    payload = response.get_json()
    assert payload["schema"]["valid"] is False
    assert "notes" in payload["schema"]["extra_fields"]


def test_validate_invalid_date(client):
    data = dict(samples.TEST_SCENARIOS[0]["expected"])
    data["date"] = "15/11/2026"
    response = client.post("/api/validate", json={"json": data})
    payload = response.get_json()
    assert payload["schema"]["valid"] is False
    assert any("date" in error for error in payload["schema"]["errors"])


def test_validate_missing_json_field_returns_400(client):
    response = client.post("/api/validate", json={"document": "{}"})
    assert response.status_code == 400


def test_validate_empty_string_returns_400(client):
    response = client.post("/api/validate", json={"json": "  "})
    assert response.status_code == 400


def test_validate_wrong_type_returns_400(client):
    response = client.post("/api/validate", json={"json": 42})
    assert response.status_code == 400


# --------------------------------------------------------------------------
# /api/tests/run
# --------------------------------------------------------------------------

def test_run_tests_all_pass(client):
    response = client.post("/api/tests/run")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["total"] == 3
    assert payload["passed"] == 3
    assert payload["failed"] == 0
    assert payload["all_passed"] is True
    for result in payload["results"]:
        assert result["syntax_valid"] is True
        assert result["schema_valid"] is True
        assert all(field["passed"] for field in result["fields"])


def test_run_tests_field_level_details(client):
    payload = client.post("/api/tests/run").get_json()
    first = payload["results"][0]
    assert {item["field"] for item in first["fields"]} == {
        "title", "date", "venue", "speaker", "topics"
    }
    assert first["checks"]


# --------------------------------------------------------------------------
# Errors and methods
# --------------------------------------------------------------------------

def test_unknown_api_endpoint_returns_json_404(client):
    response = client.get("/api/unknown")
    assert response.status_code == 404
    assert response.is_json
    assert response.get_json()["ok"] is False


def test_wrong_method_returns_405(client):
    response = client.get("/api/extract")
    assert response.status_code == 405
    assert response.get_json()["ok"] is False


def test_payload_too_large_returns_413(app_instance):
    app_instance.config["MAX_CONTENT_LENGTH"] = 200
    with app_instance.test_client() as client:
        response = client.post(
            "/api/extract",
            data=json.dumps({"paragraph": "x" * 500, "mode": "standard"}),
            content_type="application/json",
        )
    assert response.status_code == 413


def test_no_secrets_in_source():
    """Guard against accidental credential commits in application modules."""
    import pathlib

    root = pathlib.Path(__file__).resolve().parent.parent
    suspicious = ("sk-", "OPENAI_API_KEY=", "ANTHROPIC_API_KEY=", "password=")
    for name in ("app.py", "extractor.py", "prompts.py", "validator.py", "samples.py"):
        content = (root / name).read_text(encoding="utf-8")
        for marker in suspicious:
            assert marker not in content, f"{marker} found in {name}"
