"""Flask application for the Prompt-Based Information Extraction System.

Endpoints
---------
GET  /                 Web dashboard
GET  /report           Experiment report page
GET  /api/health       Health check
GET  /api/samples      Sample paragraphs, test scenarios, prompt metadata
POST /api/extract      Extract structured data from a paragraph
POST /api/validate     Validate a JSON document against the schema
POST /api/tests/run    Run the three built-in scenarios

The extraction engine is deterministic and rule-based. No external AI API is
called and no credentials are required.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Tuple

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge

import prompts
import samples
from extractor import ENGINE_NAME, ENGINE_VERSION, extract
from validator import validate_json_text_fully

MAX_PARAGRAPH_LENGTH = 5000
MAX_JSON_LENGTH = 20000
ALLOWED_MODES = ("standard", "safe")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(test_config: Dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        MAX_CONTENT_LENGTH=64 * 1024,  # 64 KB request cap
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def error_response(message: str, status: int, details: List[str] | None = None):
        payload: Dict[str, Any] = {"ok": False, "error": message}
        if details:
            payload["details"] = details
        return jsonify(payload), status

    def read_json_body() -> Tuple[Dict[str, Any] | None, Any]:
        """Return ``(body, error_response)``. Never raises on malformed JSON."""
        limit = app.config.get("MAX_CONTENT_LENGTH")
        if limit and request.content_length and request.content_length > limit:
            return None, error_response("The request body is too large.", 413)
        if not request.is_json:
            return None, error_response(
                "Request body must be JSON with Content-Type: application/json.", 415
            )
        try:
            body = request.get_json(silent=False)
        except RequestEntityTooLarge:
            return None, error_response("The request body is too large.", 413)
        except Exception:
            return None, error_response("The request body is not valid JSON.", 400)
        if not isinstance(body, dict):
            return None, error_response("The request body must be a JSON object.", 400)
        return body, None

    def run_scenario(scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run one test scenario and validate the result independently."""
        result = extract(scenario["input"], scenario["mode"])
        data = result["data"]
        raw = json.dumps(data, ensure_ascii=False)
        validation = validate_json_text_fully(raw)
        comparisons = samples.compare_fields(data, scenario["expected"])
        return {
            "id": scenario["id"],
            "name": scenario["name"],
            "description": scenario["description"],
            "mode": scenario["mode"],
            "mode_name": result["meta"]["mode_name"],
            "input": scenario["input"],
            "expected": scenario["expected"],
            "actual": data,
            "json_text": raw,
            "syntax_valid": validation["syntax"]["valid"],
            "schema_valid": validation["schema"]["valid"],
            "syntax_errors": validation["syntax"]["errors"],
            "schema_errors": validation["schema"]["errors"],
            "checks": validation["schema"]["checks"],
            "fields": comparisons,
            "passed": bool(
                validation["syntax"]["valid"]
                and validation["schema"]["valid"]
                and all(item["passed"] for item in comparisons)
            ),
            "explanation": scenario["explanation"],
            "notes": result["meta"]["notes"],
            "evidence": result["meta"]["evidence"],
            "confidence": result["meta"]["confidence"],
        }

    # ------------------------------------------------------------------
    # Pages
    # ------------------------------------------------------------------
    @app.get("/")
    def index():
        prompt_data = {
            key: {
                "id": meta["id"],
                "name": meta["name"],
                "short_name": meta["short_name"],
                "tagline": meta["tagline"],
                "description": meta["description"],
                "key_rules": meta["key_rules"],
                "template": prompts.prompt_template(key),
            }
            for key, meta in prompts.PROMPT_METADATA.items()
        }
        return render_template(
            "index.html",
            prompt_meta=prompt_data,
            engine_note=prompts.ENGINE_NOTE,
            samples=samples.SAMPLE_PARAGRAPHS,
            disclaimer=samples.DISCLAIMER,
            engine_name=ENGINE_NAME,
            engine_version=ENGINE_VERSION,
            max_length=MAX_PARAGRAPH_LENGTH,
        )

    @app.get("/report")
    def report():
        return render_template(
            "report.html",
            disclaimer=samples.DISCLAIMER,
            scenarios=samples.TEST_SCENARIOS,
            engine_name=ENGINE_NAME,
            engine_version=ENGINE_VERSION,
        )

    @app.get("/favicon.ico")
    def favicon():
        # The page declares an inline SVG icon; this avoids a noisy 404 in logs.
        return ("", 204)

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------
    @app.get("/api/health")
    def health():
        return jsonify(
            {
                "ok": True,
                "status": "healthy",
                "app": "Prompt-Based Information Extraction System",
                "engine": ENGINE_NAME,
                "engine_version": ENGINE_VERSION,
                "modes": list(ALLOWED_MODES),
                "external_api_required": False,
                "version": "1.0.0",
            }
        )

    @app.get("/api/samples")
    def get_samples():
        return jsonify(
            {
                "ok": True,
                "samples": samples.SAMPLE_PARAGRAPHS,
                "tests": [
                    {
                        "id": item["id"],
                        "name": item["name"],
                        "mode": item["mode"],
                        "description": item["description"],
                    }
                    for item in samples.TEST_SCENARIOS
                ],
                "disclaimer": samples.DISCLAIMER,
            }
        )

    @app.get("/api/prompts")
    def get_prompts():
        return jsonify(
            {
                "ok": True,
                "engine_note": prompts.ENGINE_NOTE,
                "prompts": {
                    key: {
                        "id": meta["id"],
                        "name": meta["name"],
                        "tagline": meta["tagline"],
                        "description": meta["description"],
                        "key_rules": meta["key_rules"],
                        "template": prompts.prompt_template(key),
                    }
                    for key, meta in prompts.PROMPT_METADATA.items()
                },
            }
        )

    @app.post("/api/extract")
    def api_extract():
        body, error = read_json_body()
        if error:
            return error

        paragraph = body.get("paragraph", "")
        mode = body.get("mode", "standard")

        if paragraph is None:
            paragraph = ""
        if not isinstance(paragraph, str):
            return error_response("Field 'paragraph' must be a string.", 400)
        if not isinstance(mode, str):
            return error_response("Field 'mode' must be a string.", 400)
        mode = mode.strip().lower()
        if mode not in ALLOWED_MODES:
            return error_response(
                f"Unsupported mode '{mode}'. Use 'standard' or 'safe'.", 400
            )
        if not paragraph.strip():
            return error_response(
                "The source paragraph is empty. Enter a paragraph or load a sample.", 400
            )
        if len(paragraph) > MAX_PARAGRAPH_LENGTH:
            return error_response(
                f"The paragraph exceeds the {MAX_PARAGRAPH_LENGTH:,} character limit.", 400
            )

        try:
            result = extract(paragraph, mode)
        except ValueError as exc:
            return error_response(str(exc), 400)
        except Exception:
            logger.exception("Unexpected extraction failure")
            return error_response(
                "An unexpected error occurred while extracting information. Please try again.", 500
            )

        data = result["data"]
        raw = json.dumps(data, ensure_ascii=False, indent=2)
        validation = validate_json_text_fully(raw)

        return jsonify(
            {
                "ok": True,
                "data": data,
                "json_text": raw,
                "meta": result["meta"],
                "prompt": prompts.build_prompt(mode, paragraph),
                "validation": {
                    "syntax": validation["syntax"],
                    "schema": validation["schema"],
                    "valid": validation["valid"],
                },
            }
        )

    @app.post("/api/validate")
    def api_validate():
        body, error = read_json_body()
        if error:
            return error

        if "json" not in body:
            return error_response(
                "Field 'json' is required. Send either a JSON string or an object.", 400
            )

        raw = body["json"]
        if isinstance(raw, (dict, list)):
            try:
                raw = json.dumps(raw, ensure_ascii=False)
            except (TypeError, ValueError):
                return error_response("The supplied JSON value cannot be serialised.", 400)
        elif not isinstance(raw, str):
            return error_response("Field 'json' must be a string or a JSON object.", 400)
        elif not raw.strip():
            return error_response("The JSON input is empty.", 400)
        elif len(raw) > MAX_JSON_LENGTH:
            return error_response(
                f"The JSON input exceeds the {MAX_JSON_LENGTH:,} character limit.", 400
            )

        report = validate_json_text_fully(raw)
        return jsonify(
            {
                "ok": True,
                "syntax": report["syntax"],
                "schema": report["schema"],
                "valid": report["valid"],
            }
        )

    @app.post("/api/tests/run")
    def api_run_tests():
        # The body is optional; accept an empty body for convenience.
        if request.data and not request.is_json:
            return error_response("Request body must be JSON when supplied.", 415)
        results = [run_scenario(scenario) for scenario in samples.TEST_SCENARIOS]
        passed = sum(1 for item in results if item["passed"])
        return jsonify(
            {
                "ok": True,
                "total": len(results),
                "passed": passed,
                "failed": len(results) - passed,
                "all_passed": passed == len(results),
                "results": results,
                "engine": ENGINE_NAME,
                "engine_version": ENGINE_VERSION,
            }
        )

    # ------------------------------------------------------------------
    # Error handlers
    # ------------------------------------------------------------------
    @app.errorhandler(400)
    def bad_request(_error):
        return error_response("The request could not be processed.", 400)

    @app.errorhandler(404)
    def not_found(_error):
        if request.path.startswith("/api/"):
            return error_response("API endpoint not found.", 404)
        return render_template("404.html"), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return error_response("This HTTP method is not allowed for this endpoint.", 405)

    @app.errorhandler(413)
    def payload_too_large(_error):
        return error_response("The request body is too large.", 413)

    @app.errorhandler(415)
    def unsupported_media(_error):
        return error_response("Unsupported media type. Send application/json.", 415)

    @app.errorhandler(500)
    def server_error(_error):
        logger.exception("Unhandled server error")
        return error_response("An internal server error occurred.", 500)

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
