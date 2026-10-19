# Prompt Design

This document explains the two structured prompts used by the project, why each rule exists, and how
the deterministic engine implements the same contract. It is written for an MCA practical viva.

---

## 1. What a structured prompt contains

A structured prompt is more than a question. It has six parts:

| Part | Purpose | Example from this project |
|---|---|---|
| **Role** | Tells the system what it is | "You are an information-extraction component." |
| **Task** | States the single job | "Convert the SOURCE PARAGRAPH into one JSON object." |
| **Evidence rule** | Prevents invention | "Extract only information that is explicitly supported." |
| **Schema** | Fixes the output shape | title, date, venue, speaker, topics |
| **Missing-data policy** | Defines behaviour for gaps | `null` for scalars, `[]` for topics |
| **Output constraint** | Prevents decoration | "Return JSON only, without Markdown fences." |

---

## 2. Standard Extraction prompt

```
You are an information-extraction component. Your only task is to convert the SOURCE PARAGRAPH
below into one JSON object that follows the OUTPUT SCHEMA.

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

FIELD RULES
- title: the event title as stated, or null. Do not expand it with unsupported details.
- date: a real ISO 8601 calendar date in YYYY-MM-DD format, or null.
- venue: the venue as stated, or null. A venue may be qualified with the host institution and city
  only when both are explicitly stated in the paragraph.
- speaker: the named speaker, or null. A role such as "the speaker" is not a name.
- topics: an array of explicitly listed topics. Use [] when no topics are explicitly available.
- Do not use the strings "null", "N/A", "Unknown", or "" as substitutes for JSON null.
- Do not silently convert relative or ambiguous dates into specific calendar dates.

SOURCE PARAGRAPH
"""
[[PARAGRAPH]]
"""

Return the JSON object now.
```

### Why each instruction exists

| Instruction | Reason | Failure it prevents |
|---|---|---|
| Read carefully first | Reduces missed context | Extracting from only the first sentence |
| Extract only supported information | Core anti-hallucination rule | Inventing a venue or speaker |
| Identify five specific fields | Focuses the task | Wandering summaries |
| Predefined field names | Machine-readable output | Inconsistent keys |
| null for missing scalars | Honest representation of absence | Fake values like "N/A" |
| Topics as an array | Multiple topics are naturally a list | A comma-joined string |
| Never invent or assume | Reinforcement of the evidence rule | Confident-sounding fabrications |
| JSON only, no fences | Parseable output | Markdown wrappers breaking `json.loads` |
| Follow the schema exactly | Deterministic structure | Extra or missing keys |

---

## 3. Missing-Information-Safe prompt

The safe prompt keeps all nine instructions and adds a strict block:

```
MISSING-INFORMATION-SAFE RULES (STRICT)
- Guessing is prohibited. If a value is not directly stated, return null.
- If no topics are explicitly listed, return [].
- If a date is relative ("next month") or ambiguous ("03/04/2026"), return null. Do not resolve it.
- If the event title is only a generic description ("technical workshop"), return null.
- If the speaker is described only by role, or is "not announced", return null.
- Do not infer a venue from a college name. A venue may be qualified with a host institution and city
  only when the venue itself and those details are explicitly stated.
- Prefer omission over speculation. A null value is a correct answer when the paragraph does not
  provide the fact.
```

The final rule is the philosophy of the mode: **a correct null is better than a confident guess**.

---

## 4. Comparison of the two modes

| Rule | Standard | Missing-safe |
|---|---|---|
| Extract only stated facts | Yes | Yes |
| Missing scalar value | `null` | `null` |
| No topics listed | `[]` | `[]` |
| Generic title ("technical workshop") | Rejected unless the candidate has a proper noun, or is a descriptive phrase with at least two non-generic content words | Always rejected; title stays `null` |
| Relative date ("next month") | `null` | `null` |
| Ambiguous numeric date ("03/04/2026") | `null` | `null` |
| Role-only speaker | `null` | `null` |
| Media/verification posture | Balanced | Strictest |
| Best used for | Complete, well-written paragraphs | Incomplete or uncertain paragraphs |

---

## 5. Prompt versus engine (important distinction)

The prompts in this project are **specifications**. The default extraction is performed by a
deterministic rule-based Python engine in `extractor.py`. **No language model is called and no API key
is used.** This is stated in the application interface and must be stated honestly in the viva.

How each prompt rule maps to engine code:

| Prompt instruction | Engine implementation |
|---|---|
| Read the paragraph carefully | `_clean_text()` normalises whitespace and typography |
| Extract only explicitly supported information | Every field requires a regex match from the paragraph |
| Identify five specific fields | `extract()` builds exactly those five keys |
| Return predefined field names | The output dictionary is built with fixed keys |
| null for missing scalars | Missing matches return `None` |
| Topics as an array | `extract_topics()` returns a list, `[]` when no cue exists |
| Never invent details | No default values; role-only and unannounced speakers are rejected; dates must validate |
| JSON only | The API serialises with `json.dumps`; the UI shows the raw JSON |
| Follow the schema | `validator.py` checks keys, types, date format, and topic contents |

If an optional LLM adapter is added later, it must reuse the same schema and run the response through
`validator.validate_json_text_fully()` before display. That keeps prompt design and validation
independent of the model.

---

## 6. Context engineering in this project

Context engineering is the choice of what the system sees. Here the context is deliberately minimal:

1. **Instruction block** — role, task, evidence rule, output constraint.
2. **Output schema** — the exact five fields and their types.
3. **Field rules** — how to interpret dates, venues, speakers, and topics.
4. **Source paragraph** — the only factual input.
5. **Mode rules** — the strict block in safe mode.

Nothing else is supplied: no examples that could bias the output, no external documents, no user
history. A small, precise context reduces the chance that the system "fills in" a plausible fact.

---

## 7. Copying and inspecting the prompts

- **Prompt Lab tab** shows both full prompts side by side with **Copy** buttons.
- After an extraction, the **Prompt built from the current input** panel contains the exact prompt text
  with your paragraph inserted.
- The **Copy Prompt** button on the Extractor tab copies the same text.
- `GET /api/prompts` returns both templates as JSON for programmatic use.
