# Prompt-Based Information Extraction System

**Prompt Engineering and Structured Output Generation — MCA Practical Examination (25 Marks)**

| | |
|---|---|
| **Student** | Harshad Babulal Imale |
| **Course** | Master of Computer Applications (MCA) |
| **College** | DKTE Society's Textile & Engineering Institute, Ichalkaranji |
| **Examination** | Practical Examination |
| **Subject / Experiment** | Prompt Engineering and Structured Output Generation |
| **Project Title** | Prompt-Based Information Extraction System |
| **Maximum Marks** | 25 |
| **Engine** | Deterministic rule-based extraction (no external AI API, no API key) |
| **Source repository** | *Add your GitHub URL here after publishing (see `docs/DEPLOYMENT.md`)* |
| **Live application** | *Add your Render URL here after deploying (see `docs/DEPLOYMENT.md`)* |

> **Sample data notice.** The workshop paragraph, speaker name, and all test paragraphs are
> illustrative sample data created for this practical. They do not describe a verified real-world event.

> **Note on links.** The **source code repository** and the **live application URL** are two different links.
> The repository holds the code; the live URL runs the Flask application. Both are intentionally left
> blank above until they actually exist. No URL is invented.

---

## 1. Project Overview

The application converts an unstructured workshop announcement paragraph into a validated JSON object
with exactly five fields:

```json
{
  "title": "Introduction to Generative AI and Prompt Engineering Workshop",
  "date": "2026-11-15",
  "venue": "Seminar Hall, DKTE Society's Textile & Engineering Institute, Ichalkaranji",
  "speaker": "Dr. Ananya Deshmukh",
  "topics": [
    "Prompt Design",
    "Structured JSON Output",
    "Context Engineering",
    "AI Output Validation"
  ]
}
```

It demonstrates prompt engineering (two structured prompts), context engineering, structured output,
missing-information handling, JSON syntax validation, JSON schema validation, and automated testing.

---

## 2. Aim

To design structured prompts and build a working web application that extracts only explicitly supported
information from a paragraph and represents everything missing as `null` / `[]`, without inventing facts.

## 3. Objectives

1. Design **Standard Extraction** and **Missing-Information-Safe Extraction** prompts.
2. Implement a deterministic extraction engine that works **without any external AI API key**.
3. Always return the five schema fields: `title`, `date`, `venue`, `speaker`, `topics`.
4. Use JSON `null` for missing scalars and `[]` for absent topics.
5. Validate JSON **syntax** and **schema** independently and report both.
6. Test complete, incomplete, sparse, and empty paragraphs; record actual results.
7. Document, version-control, and prepare the project for GitHub and Render deployment.

---

## 4. Features

| Feature | Description |
|---|---|
| **Sample workshop paragraph** | One-click loading of the complete illustrative paragraph (Feature A). |
| **Structured prompts** | Two prompt modes with rules, schema, and missing-data policy (Feature B). |
| **Extraction dashboard** | Responsive single-page UI with input, output, and JSON viewer (Feature C). |
| **Fixed JSON schema** | Exactly five fields, `null` / `[]` for missing data (Feature D). |
| **Rule-based engine** | Deterministic extraction with evidence tracking (Feature E). |
| **Missing-information handling** | Explicit nulls with human-readable explanations (Feature F). |
| **Three test scenarios** | Complete, missing, and sparse inputs, runnable from the UI (Feature G). |
| **Dual validation** | Separate syntax and schema validation with detailed errors (Feature H). |
| **Educational section** | Viva-ready explanations of every concept (Feature I). |
| **Experiment report page** | All 20 required report sections, printable (Feature J). |

---

## 5. Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5.3.3 (vendored locally, so it works offline)
- **Backend:** Python 3 with Flask 3.1
- **Data processing:** Python standard library (`re`, `datetime`, `json`)
- **Validation:** Python `json` module plus a custom schema validator (`validator.py`)
- **Testing:** pytest
- **Version control:** Git and GitHub
- **Deployment:** Render (Python runtime, Gunicorn)

---

## 6. Architecture

```
Browser (Bootstrap 5 UI)
        |  POST /api/extract { paragraph, mode }
        v
Flask application (app.py) ........ input validation, HTTP errors, routing
        |
        +--> prompts.py .......... structured prompt templates (specification)
        |
        +--> extractor.py ........ deterministic rule-based engine
        |
        +--> validator.py ........ JSON syntax + schema validation
        |
        v
JSON response: data, meta (evidence, notes, confidence), validation, prompt
```

**Important:** the prompt is a specification; the default extraction is performed by a deterministic
Python engine, **not** by a language model. No API key is used. See `docs/PROMPT_DESIGN.md`.

---

## 7. Folder Structure

```
prompt-information-extractor/
├── app.py                  Flask application and API endpoints
├── extractor.py            Deterministic rule-based extraction engine
├── prompts.py              Structured prompt templates and metadata
├── validator.py            JSON syntax and schema validation
├── samples.py              Sample paragraphs and the three test scenarios
├── requirements.txt        Python dependencies
├── pytest.ini              Pytest configuration
├── render.yaml             Render deployment blueprint
├── Procfile                Gunicorn start command for hosting platforms
├── runtime.txt             Python version hint for hosting platforms
├── .gitignore              Excludes virtual envs, secrets, caches
├── .gitattributes          Consistent line endings across platforms
├── .env.example            Environment template (no real secrets)
├── README.md               This file
├── templates/
│   ├── index.html          Main dashboard
│   ├── report.html         Experiment report page
│   └── 404.html            Not-found page
├── static/
│   ├── css/style.css       Academic navy/blue theme
│   ├── js/app.js           Front-end behaviour
│   └── vendor/             Bootstrap 5 CSS and JS
├── tests/
│   ├── test_extractor.py   38 tests
│   ├── test_validator.py   36 tests
│   └── test_app.py         33 tests
├── docs/
│   ├── EXPERIMENT_REPORT.md
│   ├── PROMPT_DESIGN.md
│   ├── TEST_RESULTS.md
│   ├── VIVA_QUESTIONS.md
│   ├── DEPLOYMENT.md
│   ├── DEMO_SCRIPT.md
│   └── SUBMISSION_CHECKLIST.md
└── screenshots/            Application screenshots for the report
```

---

## 8. Installation (Windows PowerShell)

Run these commands in the project folder:

```powershell
# 1. Create and activate a virtual environment
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# If activation is blocked, allow it for this session:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 2. Upgrade pip and install dependencies
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

> `requirements.txt` installs Gunicorn only on non-Windows systems. On Windows the project runs with
> the Flask development server, which is enough for the practical examination.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 9. How to Run the Flask Application

```powershell
.\.venv\Scripts\python.exe app.py
```

Then open **http://127.0.0.1:5000** in a browser.

- Change the port: `$env:PORT="8000"; .\.venv\Scripts\python.exe app.py`
- Enable debug reload while developing: `$env:FLASK_DEBUG="1"; .\.venv\Scripts\python.exe app.py`

---

## 10. How to Execute the Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Expected result (actual output from this project):

```
107 passed in 0.40s
```

Test distribution:

| Test file | Tests | Covers |
|---|---|---|
| `tests/test_extractor.py` | 38 | Extraction of all fields, dates, titles, speakers, topics, labels, edge cases |
| `tests/test_validator.py` | 36 | Syntax errors, missing/extra keys, wrong types, invalid dates, null substitutes |
| `tests/test_app.py` | 33 | Pages, health, extract, validate, tests-run endpoints, error handling, secrets guard |

See `docs/TEST_RESULTS.md` for the recorded output.

---

## 11. Example Input and Output

**Input**

> DKTE Society's Textile & Engineering Institute, Ichalkaranji, will organize the Introduction to
> Generative AI and Prompt Engineering Workshop on 15 November 2026 in the Seminar Hall.
> Dr. Ananya Deshmukh will be the speaker. The workshop will cover Prompt Design, Structured JSON
> Output, Context Engineering, and AI Output Validation.

**Output**

```json
{
  "title": "Introduction to Generative AI and Prompt Engineering Workshop",
  "date": "2026-11-15",
  "venue": "Seminar Hall, DKTE Society's Textile & Engineering Institute, Ichalkaranji",
  "speaker": "Dr. Ananya Deshmukh",
  "topics": [
    "Prompt Design",
    "Structured JSON Output",
    "Context Engineering",
    "AI Output Validation"
  ]
}
```

**Missing information** — "The college will conduct a Python programming workshop on 20 December 2026.
Students will learn file handling and exception handling."

```json
{
  "title": "Python programming workshop",
  "date": "2026-12-20",
  "venue": null,
  "speaker": null,
  "topics": ["file handling", "exception handling"]
}
```

---

## 12. API Endpoints

| Method | Endpoint | Body | Description |
|---|---|---|---|
| GET | `/` | — | Main dashboard |
| GET | `/report` | — | Experiment report page |
| GET | `/api/health` | — | Health status and engine information |
| GET | `/api/samples` | — | Sample paragraphs and test definitions |
| GET | `/api/prompts` | — | Prompt templates and metadata |
| POST | `/api/extract` | `{"paragraph": "...", "mode": "standard\|safe"}` | Extract structured data |
| POST | `/api/validate` | `{"json": "<string or object>"}` | Validate syntax and schema |
| POST | `/api/tests/run` | `{}` (optional) | Run the three test scenarios |

Status codes: `200` success, `400` invalid input, `404` unknown endpoint, `405` wrong method,
`413` payload too large, `415` wrong content type.

Example:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/api/extract `
  -ContentType "application/json" `
  -Body '{"paragraph":"A Python workshop will be held on 5 May 2027 in the Computer Lab.","mode":"standard"}'
```

---

## 13. Deployment

Full step-by-step instructions are in **[`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)**.

Short version for Render:

1. Push this repository to GitHub.
2. On <https://render.com>, create a **New Web Service** and connect the repository.
3. Render detects `render.yaml`, or set manually:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60`
   - **Health check path:** `/api/health`
4. After deployment, verify `https://YOUR-APP.onrender.com/api/health` and the main page.

The live URL does not exist until you actually deploy. Add it to the table at the top of this README.

---

## 14. Screenshots

Screenshots are stored in the [`screenshots/`](screenshots/) folder. Suggested captures are listed in
`screenshots/README.md`. The Experiment Report page has a screenshots section ready for insertion.

---

## 15. Known Limitations

- Rule-based extraction covers common announcement patterns, not unrestricted natural language.
- Indirect or implicit statements may produce `null` even when a human could infer the value.
- Relative dates ("next month") are intentionally **not** resolved.
- Venue is extracted only from explicit venue phrases; a bare college name is not used as a venue.
- No database and no authentication — each request is processed in memory for a single user.
- Gunicorn is not installed on Windows; the Flask development server is used locally.

---

## 16. Security and Privacy

- No API keys, passwords, or tokens are hardcoded anywhere in the project.
- `.env` files and credentials are excluded by `.gitignore`; `.env.example` contains placeholders only.
- User paragraphs are processed in memory and are not stored.
- Submitted text is treated as data, never executed as code.
- Optional LLM integration is kept separate and disabled by default.
- A pytest guard checks the source files for accidental credential strings.

---

## 17. Documentation Index

| Document | Purpose |
|---|---|
| [`docs/EXPERIMENT_REPORT.md`](docs/EXPERIMENT_REPORT.md) | Full 20-section experiment report |
| [`docs/PROMPT_DESIGN.md`](docs/PROMPT_DESIGN.md) | Prompt design, both modes, engine mapping |
| [`docs/TEST_RESULTS.md`](docs/TEST_RESULTS.md) | Actual recorded pytest results |
| [`docs/VIVA_QUESTIONS.md`](docs/VIVA_QUESTIONS.md) | Viva questions with answers |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | GitHub and Render instructions |
| [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) | 5-minute demonstration script |
| [`docs/SUBMISSION_CHECKLIST.md`](docs/SUBMISSION_CHECKLIST.md) | Requirement-to-marks checklist |

---

## 18. Student and Course Details

- **Name:** Harshad Babulal Imale
- **Course:** Master of Computer Applications (MCA)
- **College:** DKTE Society's Textile & Engineering Institute, Ichalkaranji
- **Examination:** Practical Examination
- **Subject / Experiment:** Prompt Engineering and Structured Output Generation
- **Maximum Marks:** 25
- **Project:** Prompt-Based Information Extraction System
