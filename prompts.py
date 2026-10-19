"""Structured prompt templates used by the Prompt-Based Information Extractor.

IMPORTANT ENGINE NOTE
---------------------
The default extraction engine in this project is deterministic and rule-based
(see ``extractor.py``).  The prompts below are *engineering artefacts*: they
document the exact instructions and output contract that the extraction layer
is designed around.  They are displayed and copyable in the web interface, but
they are **not** sent to a language model in the default build.  No API key is
required or used.  If an LLM adapter is added later, it must validate the
model response independently with ``validator.py`` before displaying it.
"""

from __future__ import annotations

PROMPT_VERSION = "1.0"

PARAGRAPH_PLACEHOLDER = "[[PARAGRAPH]]"

OUTPUT_SCHEMA_TEXT = """{
  "title": string | null,
  "date": "YYYY-MM-DD" | null,
  "venue": string | null,
  "speaker": string | null,
  "topics": [string]
}"""

STANDARD_PROMPT = """You are an information-extraction component. Your only task is to convert the SOURCE PARAGRAPH below into one JSON object that follows the OUTPUT SCHEMA.

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
{schema}

FIELD RULES
- title: the event title as stated, or null. Do not expand it with unsupported details.
- date: a real ISO 8601 calendar date in YYYY-MM-DD format, or null.
- venue: the venue as stated, or null. A venue may be qualified with the host institution and city only when both are explicitly stated in the paragraph.
- speaker: the named speaker, or null. A role such as "the speaker" is not a name.
- topics: an array of explicitly listed topics. Use [] when no topics are explicitly available.
- Do not use the strings "null", "N/A", "Unknown", or "" as substitutes for JSON null.
- Do not silently convert relative or ambiguous dates into specific calendar dates.

SOURCE PARAGRAPH
\"\"\"
{paragraph}
\"\"\"

Return the JSON object now."""

MISSING_SAFE_PROMPT = """You are an information-extraction component working in MISSING-INFORMATION-SAFE mode. Your only task is to convert the SOURCE PARAGRAPH below into one JSON object that follows the OUTPUT SCHEMA.

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
{schema}

MISSING-INFORMATION-SAFE RULES (STRICT)
- Guessing is prohibited. If a value is not directly stated, return null.
- If no topics are explicitly listed, return [].
- If a date is relative ("next month") or ambiguous ("03/04/2026"), return null. Do not resolve it.
- If the event title is only a generic description ("technical workshop"), return null.
- If the speaker is described only by role, or is "not announced", return null.
- Do not infer a venue from a college name. A venue may be qualified with a host institution and city only when the venue itself and those details are explicitly stated.
- Prefer omission over speculation. A null value is a correct answer when the paragraph does not provide the fact.

SOURCE PARAGRAPH
\"\"\"
{paragraph}
\"\"\"

Return the JSON object now."""

PROMPT_METADATA = {
    "standard": {
        "id": "standard-extraction-v1",
        "name": "Standard Extraction",
        "short_name": "Standard",
        "tagline": "Extract all information that is explicitly available.",
        "description": (
            "Balanced extraction. It uses the explicit cues in the paragraph and "
            "allows a documented low-confidence title fallback. Missing values are "
            "still returned as null; the model is never allowed to invent facts."
        ),
        "key_rules": [
            "Extract only explicitly supported values.",
            "Use null for missing scalar values.",
            "Use [] when no topics are listed.",
            "Return JSON only, with no extra keys.",
            "Ambiguous or relative dates stay null.",
        ],
        "template": STANDARD_PROMPT,
    },
    "safe": {
        "id": "missing-safe-extraction-v1",
        "name": "Missing-Information-Safe Extraction",
        "short_name": "Missing-safe",
        "tagline": "Prefer omission over speculation when evidence is weak.",
        "description": (
            "Strict extraction. It forbids weak guesses: generic titles, role-only "
            "speakers, relative or ambiguous dates, and inferred venues all become "
            "null. This is the recommended mode for incomplete paragraphs."
        ),
        "key_rules": [
            "Guessing is prohibited; omit uncertain values.",
            "Generic event descriptions are not accepted as titles.",
            "Relative and ambiguous dates are null.",
            "Role-only or unannounced speakers are null.",
            "Use [] when no topics are explicitly listed.",
        ],
        "template": MISSING_SAFE_PROMPT,
    },
}

ENGINE_NOTE = (
    "The prompt text is a structured specification. In this build the extraction "
    "itself is performed by a deterministic rule-based Python engine, not by a "
    "language model. No external AI API is called and no API key is used. "
    "Prompt design and deterministic extraction are therefore related but separate: "
    "the prompt states the contract; the engine implements it."
)


def build_prompt(mode: str, paragraph: str) -> str:
    """Return the full prompt text for *mode* with *paragraph* inserted.

    ``str.replace`` is used instead of ``str.format`` so that the JSON braces in
    the schema do not need escaping.
    """
    if mode not in PROMPT_METADATA:
        raise ValueError(f"Unsupported prompt mode: {mode!r}")
    template = PROMPT_METADATA[mode]["template"]
    return (
        template.replace("{schema}", OUTPUT_SCHEMA_TEXT)
        .replace(PARAGRAPH_PLACEHOLDER, paragraph.strip())
    )


def prompt_template(mode: str) -> str:
    """Return the template with readable placeholders, for display/comparison."""
    if mode not in PROMPT_METADATA:
        raise ValueError(f"Unsupported prompt mode: {mode!r}")
    return PROMPT_METADATA[mode]["template"].replace("{schema}", OUTPUT_SCHEMA_TEXT)
