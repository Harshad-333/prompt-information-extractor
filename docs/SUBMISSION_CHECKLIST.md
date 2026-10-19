# Submission Checklist — Mapping Requirements to Marks

**Project:** Prompt-Based Information Extraction System
**Student:** Harshad Babulal Imale (MCA)
**Maximum marks:** 25

Every row below maps a requirement from the question paper to an artefact in this project and its status.

---

## A. Functional requirements

| Ref | Requirement | Where it is implemented | Status |
|---|---|---|---|
| A | Sample workshop paragraph + load button | `samples.py`, **Load Sample Paragraph** button | Done |
| B | Structured prompt section, two modes, copy + comparison | `prompts.py`, **Prompt Lab** tab | Done |
| C | Extraction interface with all controls | `templates/index.html`, `static/js/app.js` | Done |
| D | Five-field JSON schema | `extractor.py`, `validator.py`, schema card in UI | Done |
| E | Reliable rule-based extraction engine | `extractor.py` | Done |
| F | Missing-information handling + minimal paragraph | `extractor.py` notes, `test_no_workshop_details_paragraph` | Done |
| G | Three test scenarios + Run All Tests | `samples.py`, `POST /api/tests/run`, **Test Suite** tab | Done |
| H | JSON syntax + schema validation | `validator.py`, **Schema & Validation** tab | Done |
| I | Educational explanation section | **Learn** tab | Done |
| J | Experiment report with 20 sections | `templates/report.html`, `docs/EXPERIMENT_REPORT.md` | Done |

## B. Interface quality

| Requirement | Status |
|---|---|
| Responsive navigation with tabs | Done (Bootstrap 5 tabs, sticky nav) |
| Input and output panels | Done |
| Formatted JSON viewer | Done (custom syntax highlighting) |
| Status indicators for syntax and schema | Done (independent pills) |
| Clear success and error messages | Done (alerts + field-level errors) |
| Test results table | Done (per-test cards with field tables) |
| Prompt comparison section | Done (side-by-side cards + comparison table) |
| Documentation section | Done (README + `docs/`, in-app Learn tab) |
| Footer with project and student details | Done |
| Accessibility (labels, keyboard, contrast) | Done (labels, aria-live, focus styles, skip link) |
| Every visible button works | Done (verified — no decorative controls) |

## C. Backend and API

| Requirement | Status |
|---|---|
| `GET /` serves the interface | Done |
| `POST /api/extract` | Done |
| `POST /api/validate` | Done |
| `GET /api/health` | Done |
| Proper HTTP status codes | Done (200/400/404/405/413/415/500) |
| Input validation and length limits | Done (5,000 chars, 20,000 JSON chars, 64 KB body) |
| Malformed JSON and unexpected errors handled | Done |
| No unsafe evaluation of user input | Done (no `eval`, data only) |

## D. Security and privacy

| Requirement | Status |
|---|---|
| No hardcoded keys, passwords, or tokens | Done |
| `.env` never committed | Done (`.gitignore` + `.env.example`) |
| Server-side input validation | Done |
| Submitted text not executed as code | Done |
| User paragraphs not stored | Done (in-memory only) |
| Optional AI integration kept separate | Done (documented, disabled, no SDK installed) |
| LLM response would be validated before display | Documented in `docs/PROMPT_DESIGN.md` |

## E. Testing

| Requirement | Status |
|---|---|
| pytest tests for engine, validator, API | Done — `tests/test_extractor.py`, `test_validator.py`, `test_app.py` |
| Complete workshop information | Done |
| Missing venue and speaker | Done |
| Empty paragraph | Done |
| Sparse / ambiguous paragraph | Done |
| Invalid JSON | Done |
| Missing required key | Done |
| Unexpected extra key | Done |
| Wrong data type | Done |
| Invalid date | Done |
| Invalid topics array | Done |
| API malformed data | Done |
| API health endpoint | Done |
| **All tests pass** | **107 passed** |

## F. Documentation

| Requirement | Status |
|---|---|
| Comprehensive README | Done |
| Aim and objectives | Done |
| Features | Done |
| Technology stack | Done |
| Architecture | Done |
| Folder structure | Done |
| Windows PowerShell installation | Done |
| Virtual environment setup | Done |
| Dependency installation | Done |
| How to run the app | Done |
| How to run tests | Done |
| Example input and output | Done |
| API endpoint descriptions | Done |
| Deployment instructions | Done (`docs/DEPLOYMENT.md`) |
| Screenshot placeholders | Done (`screenshots/README.md`, report section 15) |
| Known limitations | Done |
| Student and course details | Done |
| `.gitignore` excludes secrets and caches | Done |
| Deployment configuration | Done (`render.yaml`, `Procfile`, `runtime.txt`) |
| No secrets committed | Done (verified) |

## G. GitHub and deployment

| Requirement | Status |
|---|---|
| Project prepared for publication | Done (ready to commit) |
| Repository URL provided | **Pending — add after you publish** |
| Live application URL provided | **Pending — add after you deploy** |
| No invented URLs, statuses, or results | Done — all placeholders marked |

## H. Final deliverables

| Deliverable | Status |
|---|---|
| 1. Complete working project | Done |
| 2. Responsive user interface | Done |
| 3. Structured prompt templates | Done |
| 4. Working extraction engine | Done |
| 5. Missing-information handling | Done |
| 6. JSON syntax + schema validation | Done |
| 7. Three test scenarios | Done |
| 8. Automated pytest tests | Done (107) |
| 9. Experiment report | Done |
| 10. Prompt design documentation | Done |
| 11. Viva questions and answers | Done |
| 12. README and installation instructions | Done |
| 13. GitHub publication instructions | Done (`docs/DEPLOYMENT.md`) |
| 14. Deployment instructions | Done |
| 15. Actual test results | Done (`docs/TEST_RESULTS.md`) |
| 16. Demonstration script | Done (`docs/DEMO_SCRIPT.md`) |
| 17. Requirement-to-marks checklist | This document |

---

## Before submitting

1. Run `.\\.venv\\Scripts\\python.exe -m pytest -q` and confirm **107 passed**.
2. Run the app and execute **Run All Tests** — confirm **3 / 3 passed**.
3. Capture the screenshots listed in `screenshots/README.md`.
4. Publish to GitHub and paste the real repository URL into the README.
5. Deploy to Render, verify `/api/health`, and paste the real live URL into the README.
6. Print the **Experiment Report** page to PDF for submission.
