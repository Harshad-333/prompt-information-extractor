# Demonstration Script

A short, spoken walkthrough for the practical examination. Total time: about 5 minutes.

---

## Before you start

```powershell
.\.venv\Scripts\python.exe app.py
```

Open <http://127.0.0.1:5000>. Keep a terminal ready for the test command.

---

## Step 1 — Introduce the project (30 seconds)

> "This is a Prompt-Based Information Extraction System. It converts a workshop paragraph into a
> five-field JSON record. The fields are title, date, venue, speaker, and topics. The system is built
> around two structured prompts and a deterministic rule-based engine, so it works without an API key.
> Missing information is represented as null, never invented."

---

## Step 2 — Show the complete sample (60 seconds)

1. Click **Load Sample Paragraph**.
2. Point out the prompt mode selector: **Standard Extraction**.
3. Click **Extract Information**.
4. Show the result and the two status pills: **Syntax: valid** and **Schema: valid**.
5. Point to the **Field summary** table and mention that each row shows the evidence phrase used.

> "Every value comes from an explicit phrase in the paragraph. The evidence column shows which phrase."

---

## Step 3 — Show missing-information handling (60 seconds)

1. Click **Load Missing-Info Example**.
2. Click **Extract Information**.
3. Show that `venue` and `speaker` are `null`.
4. Read the **Missing-information notes** aloud.

> "The paragraph names no venue and no speaker. Instead of guessing, the engine returns JSON null and
> explains exactly why. This is the missing-information contract."

---

## Step 4 — Show the sparse case (45 seconds)

1. Click **Load Sparse Example**.
2. Set the mode to **Missing-Information-Safe Extraction**.
3. Click **Extract Information**.
4. Show that everything is `null` / `[]`.

> "'Next month' is not a calendar date. 'Technical workshop' is not a specific title. The speaker is
> explicitly not announced. Guessing is prohibited in safe mode, so every field stays empty."

---

## Step 5 — Run the three required tests (45 seconds)

1. Open the **Test Suite** tab.
2. Click **Run All Tests**.
3. Show **3 passed / 0 failed** and the field-level correctness table.

> "The test runner uses the same engine and validator. It checks JSON syntax, the schema, and every
> expected field for each of the three scenarios."

---

## Step 6 — Show validation (45 seconds)

1. Open the **Schema & Validation** tab.
2. Click **Load invalid example**, then **Validate JSON**.
3. Show that syntax is valid but schema is invalid, and read the four errors.

> "Syntax and schema are checked separately. This document is valid JSON, but it has an extra key,
> a non-null substitute for null, a wrong date format, and a topic that is not a string."

---

## Step 7 — Show the automated tests in a terminal (30 seconds)

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Show the final line:

```
107 passed in 0.40s
```

> "The project has 107 automated tests covering the engine, the validator, and the API."

---

## Step 8 — Close (20 seconds)

> "To summarise: structured prompt engineering defines the contract; a deterministic engine implements
> it; the validator enforces the schema; and missing information is reported honestly as null. The
> project also has an experiment report page, GitHub-ready documentation, and a Render deployment
> configuration."

---

## Likely examiner questions — quick answers

| Question | Answer |
|---|---|
| Which file contains the extraction logic? | `extractor.py` |
| Which file validates the output? | `validator.py` |
| Which file holds the prompts? | `prompts.py` |
| Does it call an AI API? | No — deterministic rule-based engine, no API key |
| How many tests pass? | 107 |
| What happens with an empty paragraph? | The API returns HTTP 400 with a clear message |
| What if the JSON is malformed? | Syntax validation fails and schema validation is skipped with an explanation |
| Where is the missing-information explanation? | In the notes returned by the engine and shown in the UI |
