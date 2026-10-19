# Experiment Report

## Prompt-Based Information Extraction System

**Prompt Engineering and Structured Output Generation**

| Field | Detail |
|---|---|
| Student | Harshad Babulal Imale |
| Course | Master of Computer Applications (MCA) |
| College | DKTE Society's Textile & Engineering Institute, Ichalkaranji |
| Examination | Practical Examination |
| Subject / Experiment | Prompt Engineering and Structured Output Generation |
| Maximum Marks | 25 |
| Engine | Deterministic rule-based extraction (no external AI API) |

> **Sample data notice.** The workshop paragraph, speaker name, and all test paragraphs are illustrative
> sample data created for this practical examination. They do not describe a verified real-world event.

---

## 1. Experiment Title

**Prompt-Based Information Extraction System: structured prompt design, deterministic extraction, and JSON schema validation.**

## 2. Aim

To design a structured prompt and build a web application that converts an unstructured workshop
paragraph into a validated five-field JSON object, correctly representing missing information as
`null` or `[]`.

## 3. Objectives

1. Design two structured prompts: Standard Extraction and Missing-Information-Safe Extraction.
2. Implement a deterministic extraction engine that needs no external AI API key.
3. Produce a JSON object with exactly five fields: `title`, `date`, `venue`, `speaker`, `topics`.
4. Represent missing scalar values as `null` and missing topics as `[]`.
5. Validate JSON syntax and schema independently with clear error messages.
6. Test complete, incomplete, sparse, and empty paragraphs and report actual results.
7. Document the work and prepare it for GitHub publication and deployment.

## 4. Problem Statement

Workshop announcements are written as free-form prose. The same facts appear in different orders and
phrasings, and some facts are often missing. Extracting them manually is slow and inconsistent.
A naive extractor may invent a venue, turn a role into a speaker name, or convert "next month" into a
false calendar date. The problem is to extract only explicitly supported facts and to represent
everything else honestly as `null` or `[]`.

## 5. Software and Hardware Requirements

| Type | Requirement |
|---|---|
| Operating system | Windows 10/11, Linux, or macOS |
| Language | Python 3.10 or newer (developed and tested with Python 3.14) |
| Backend framework | Flask 3.1 |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5.3 (vendored locally) |
| Data processing | Python standard library (`re`, `datetime`) |
| Validation | Python `json` module plus the custom `validator.py` |
| Testing | pytest 9 |
| Version control | Git, GitHub |
| Deployment | Render (Python runtime, Gunicorn) |
| Hardware | Any laptop with 4 GB RAM; no GPU required |
| Network | Not required at runtime; no external AI service is called |

## 6. Theory

**Prompt engineering** is the discipline of writing precise instructions for an AI system. A structured
prompt defines the role, the task, the evidence rule, the output schema, and the missing-data policy.

**Context engineering** is selecting the information supplied to the system. Here the context is the
paragraph, the five-field schema, the field rules, and the "extract only explicitly supported
information" rule.

**Structured output** means returning machine-readable JSON with fixed keys rather than free text,
making the result testable, comparable, and storable.

**Missing information** is represented with JSON `null` (and `[]` for topics). `null` is a distinct
JSON type meaning "no value"; the strings `"N/A"` or `"Unknown"` are ambiguous and are rejected.

**Validation** has two independent layers. Syntax validation checks that the text parses as JSON.
Schema validation checks the parsed object's keys, types, and value formats. Passing one does not
imply passing the other.

**Rule-based versus model-based extraction.** This project's default engine is deterministic and
rule-based. It does not call a language model. The prompts are structured specifications that state
the contract; the engine implements that contract with regular expressions and explicit rules. An
optional LLM adapter could be added later and would be validated by the same schema validator.

## 7. Algorithm

1. Accept the paragraph and the selected prompt mode.
2. Reject empty input, over-length input, or an unsupported mode with a clear error.
3. Normalise whitespace and typographic characters.
4. Split the paragraph into sentences, protecting abbreviations such as "Dr.".
5. Extract the date with ordered patterns (ISO, day-month-year, month-day-year). Reject invalid,
   partial, relative, and ambiguous dates.
6. Extract the title using verb patterns, an "event on topic" pattern, and a sentence-level event
   phrase; apply documented specificity rules for the selected mode.
7. Extract the venue only from explicit venue phrases; optionally qualify it with an explicitly stated
   host institution and city.
8. Extract the speaker only from a named-person pattern; reject role-only and "not announced" references.
9. Extract topics after an explicit cue such as "will cover" or "topics include", splitting on commas
   and "and".
10. Build the five-field object with `null` / `[]` for absent values.
11. Validate syntax, then validate the schema, then return the result with evidence and notes.

## 8. System Workflow

```
Browser (Bootstrap UI)
      |
      |  POST /api/extract  { paragraph, mode }
      v
Flask route (app.py) -- input validation, HTTP error handling
      |
      v
Extraction engine (extractor.py) -- rule-based, deterministic
      |
      v
Five-field dict -- json.dumps
      |
      v
Validator (validator.py) -- syntax check, then schema check
      |
      v
JSON response -- UI renders JSON, status pills, evidence, notes
```

## 9. Sample Input

> DKTE Society's Textile & Engineering Institute, Ichalkaranji, will organize the Introduction to
> Generative AI and Prompt Engineering Workshop on 15 November 2026 in the Seminar Hall.
> Dr. Ananya Deshmukh will be the speaker. The workshop will cover Prompt Design, Structured JSON
> Output, Context Engineering, and AI Output Validation.

## 10. Structured Prompt

The Standard Extraction prompt contains nine explicit instructions, the output schema, field rules,
and the source paragraph. The full text of both prompts is in `docs/PROMPT_DESIGN.md` and in the
application's **Prompt Lab** tab.

```
You are an information-extraction component. Your only task is to convert the SOURCE PARAGRAPH below
into one JSON object that follows the OUTPUT SCHEMA.

INSTRUCTIONS
1. Read the supplied paragraph carefully before extracting anything.
2. Extract only information that is explicitly supported by the paragraph.
3. Identify the workshop title, date, venue, speaker, and topics.
4. Return a JSON object with exactly these predefined field names: title, date, venue, speaker, topics.
5. Represent every missing or unavailable scalar value as null.
6. Represent topics as an array of strings.
7. Never invent details, infer a speaker, or fill gaps using assumptions.
8. Return JSON only, without Markdown code fences or explanatory text.
9. Follow the defined output schema exactly. Do not add extra keys.

OUTPUT SCHEMA
{
  "title": string | null,
  "date": "YYYY-MM-DD" | null,
  "venue": string | null,
  "speaker": string | null,
  "topics": [string]
}

SOURCE PARAGRAPH
"""
[[PARAGRAPH]]
"""

Return the JSON object now.
```

## 11. Expected JSON Output

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

## 12. Missing-Information Handling

For the paragraph *"The college will conduct a Python programming workshop on 20 December 2026.
Students will learn file handling and exception handling."*, the venue and speaker are not stated.
The engine returns `null` for both:

- **venue is null** because no explicit venue phrase such as "in the Seminar Hall" was found.
  "The college" is a host reference, not a venue, and is not converted into one.
- **speaker is null** because no person's name was supplied. A role such as "the speaker" is not a name.

For *"A technical workshop will be organized next month. The speaker has not been announced."*, the
relative date is not resolved, the generic description is not accepted as a specific title, and the
unannounced speaker produces `null`.

## 13. Test Case Table

| Test | Input focus | Mode | Expected outcome | Actual result |
|---|---|---|---|---|
| TEST 1 – Complete Information | All five fields stated | `standard` | All five fields populated | **PASS** |
| TEST 2 – Missing Information | Venue and speaker absent | `standard` | `venue` and `speaker` are `null` | **PASS** |
| TEST 3 – Sparse / Ambiguous | Relative date, generic title, unannounced speaker | `safe` | All fields `null` / `[]` | **PASS** |
| Additional – No workshop details | Unrelated paragraph | `standard` | All fields `null` / `[]` | **PASS** |

Actual extracted values, validation results, and field-by-field comparisons are recorded in
`docs/TEST_RESULTS.md`.

## 14. Validation Results

Validation is reported in two independent layers. Every extraction displays a **syntax** pill and a
**schema** pill, plus each individual schema check.

The schema validator checks:

1. JSON syntax validity.
2. Root value is an object.
3. All five required keys exist.
4. No extra keys are present.
5. Each field has the correct type.
6. The date is a real ISO `YYYY-MM-DD` calendar date or `null`.
7. `topics` contains only non-empty strings.
8. Missing scalars use real JSON `null` (not `"N/A"`, `"Unknown"`, or `""`).
9. The output can be serialised back to valid JSON.

Automated coverage: 36 validator tests plus 33 API tests, all passing (see `docs/TEST_RESULTS.md`).

## 15. Screenshots

Screenshots are captured from the running application and stored in the `screenshots/` folder:

1. `01-extractor-complete.png` — sample paragraph loaded and all five fields extracted.
2. `02-missing-information.png` — venue and speaker shown as `null` with explanatory notes.
3. `03-test-suite.png` — all three required scenarios passing.
4. `04-validation.png` — schema validation detecting deliberate errors.
5. `05-report.png` — the experiment report page.

Instructions for capturing and inserting screenshots are in `screenshots/README.md`.

## 16. Result

The application starts successfully and processes all required paragraphs. The complete paragraph
produces all five expected fields. The incomplete paragraph returns `null` for the missing venue and
speaker without inventing values. The sparse paragraph returns all `null` / `[]`. Invalid JSON and
schema violations are detected and explained. The automated pytest suite reports **107 passed**.

## 17. Limitations

- Rule-based extraction covers common announcement patterns, not unrestricted natural language.
- Indirect or implicit statements may produce `null` even when a human could infer the value.
- Relative dates ("next month") are intentionally not resolved.
- A venue is extracted only from explicit venue phrases; a bare college name is not used as a venue.
- No database and no authentication; each request is processed in memory for a single user.
- Gunicorn is not installed on Windows; the Flask development server is used locally.

## 18. Future Scope

- Add an optional, environment-configured LLM adapter with independent response validation.
- Support additional event types and extra schema fields.
- Export records to CSV or a database.
- Add multi-paragraph batch extraction.
- Add confidence calibration and a human reviewer approval step.

## 19. Conclusion

The experiment shows that a well-specified structured prompt combined with a transparent deterministic
engine can produce reliable, schema-valid JSON from unstructured text. Representing missing values as
`null` and separating syntax validation from schema validation makes the output honest, verifiable,
and testable. The project meets all stated objectives and passes 107 automated tests.

## 20. Viva Questions with Answers

See `docs/VIVA_QUESTIONS.md` for the full list. Key questions:

| Question | Answer |
|---|---|
| What is prompt engineering? | Writing precise instructions that define the task, context, constraints, and output format for an AI system. |
| What is structured-output prompting? | Asking for a fixed machine-readable format, such as JSON with named fields, instead of free text. |
| Why use JSON? | It is language-independent, easy to parse, and easy to validate. |
| Why `null` instead of `"N/A"`? | `null` is a distinct JSON type meaning "no value"; `"N/A"` is a string that can be mistaken for real data. |
| Difference between syntax and schema validation? | Syntax checks that the text parses as JSON; schema checks keys, types, and value formats. |
| Does this project use an LLM? | No. The default engine is deterministic and rule-based. The prompt is a specification. |
| How is hallucination reduced? | Evidence-only rules, explicit pattern matching, null defaults, and independent validation. |
| Why is "next month" returned as null? | It has no unambiguous calendar date; converting it would invent information. |
| What is context engineering? | Deciding what information and instructions to provide so the system has exactly the relevant context. |
| Why keep the schema fixed? | Comparability, testability, and predictable downstream processing. |
