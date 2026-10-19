# Viva Questions and Answers

**Project:** Prompt-Based Information Extraction System
**Student:** Harshad Babulal Imale (MCA)

Answers are written to be spoken aloud in a viva: short, correct, and honest about what the project
does and does not do.

---

## A. Prompt engineering

**1. What is prompt engineering?**
It is the practice of writing clear instructions for an AI system so that the response is accurate,
relevant, and usable. A good prompt defines the task, the context, the constraints, and the output format.

**2. What are the parts of a well-structured prompt?**
Role, task, evidence rule, output schema, missing-data policy, and output constraints (for example,
"JSON only, no Markdown fences").

**3. What is context engineering?**
Deciding what information and instructions the system receives. In this project the context is the
paragraph, the five-field schema, the field rules, and the rule to extract only supported facts.

**4. Why does the prompt say "extract only explicitly supported information"?**
It is the main anti-hallucination rule. Without it, a model (or a careless parser) may fill gaps with
plausible-sounding but unsupported facts.

**5. What is the difference between the two prompt modes?**
Standard Extraction is balanced and allows a documented title fallback. Missing-Information-Safe
Extraction is strict: it forbids weak guesses, rejects generic titles, keeps relative or ambiguous
dates as `null`, and treats role-only or unannounced speakers as `null`.

**6. Does this project call a language model?**
No. The default engine is deterministic and rule-based. The prompts are specifications; the engine
implements them. No API key is used. This is stated in the interface and must be stated honestly.

## B. Structured output

**7. What is structured-output prompting?**
Asking for a fixed machine-readable format, such as JSON with named fields, instead of free text.

**8. Why is structured output useful?**
It is parseable, validatable, comparable across records, and easy to store or display in a table.

**9. Why exactly five fields?**
A fixed schema makes every record the same shape, which allows automated testing and predictable
downstream use. Extra fields would break that contract.

**10. What happens if a field is missing in the paragraph?**
The field key is still present and its value is JSON `null` (or `[]` for topics).

## C. Missing information

**11. Why use `null` instead of `"N/A"` or `"Unknown"`?**
`null` is a distinct JSON type that unambiguously means "no value". `"N/A"` is a string that could be
real data, so it can hide missing information.

**12. Why is an empty array used for topics?**
Topics are inherently a list. `[]` means "the list is empty", which is the correct representation
when no topics are stated.

**13. Why is "next month" not converted into a date?**
The paragraph does not give an unambiguous calendar date. Resolving it would require inventing a
reference point, so the correct output is `null`.

**14. Why is a numeric date like "03/04/2026" rejected?**
It is ambiguous: it could be 3 April or 4 March. The schema requires a specific ISO date, so the
engine returns `null` rather than guessing.

**15. The paragraph says "the speaker has not been announced". Why is speaker null?**
No person's name is supplied. A role or a statement of non-announcement is not a name, so `null` is
the honest answer.

## D. Validation

**16. What is JSON syntax validation?**
Checking that the text is well-formed JSON: correct braces, quotes, commas, and value types, so it
parses with `json.loads`.

**17. What is JSON schema validation?**
Checking that the parsed object follows the agreed structure: the five required keys, no extra keys,
correct types, a valid ISO date, and topic strings.

**18. Why are they reported separately?**
They answer different questions. A document can be valid JSON and still violate the schema, or be
schema-shaped but fail to parse. Reporting only one gives false confidence.

**19. How does the validator handle invalid dates?**
It checks the `YYYY-MM-DD` format and then uses `datetime.date.fromisoformat` to confirm the date is a
real calendar date. "31 February" is rejected.

**20. How do you check that output is serialisable?**
The validator calls `json.dumps(value)` on the object. If that raises, the check fails.

## E. Extraction engine

**21. How does the engine extract the date?**
It tries ordered patterns: ISO `YYYY-MM-DD`, day-month-year with a month name, and month-day-year.
Each candidate is validated as a real calendar date. Relative and ambiguous references are rejected.

**22. How does the engine extract the venue?**
Only from an explicit venue phrase such as "in the Seminar Hall" or "at the Auditorium". It may add
an explicitly stated host institution and city, but it never infers a venue from a college name alone.

**23. How does the engine extract topics?**
It looks for an explicit cue ("will cover", "topics include", "will learn") and splits the following
list on commas and "and", removing duplicates.

**24. Why is a rule-based engine used instead of an LLM?**
It is deterministic, runs without an API key, is easy to explain in a viva, and shows exactly why each
value was extracted. The trade-off is lower coverage of unusual phrasing.

**25. How does the engine avoid hallucination?**
Every field requires an actual pattern match in the paragraph. There are no default values, role-only
speakers are rejected, generic titles are rejected, and dates must validate.

## F. Software engineering

**26. What does the Flask backend do?**
It serves the dashboard, validates request input, calls the extraction engine and validator, and
returns JSON. It also handles malformed requests and HTTP errors gracefully.

**27. How are user inputs validated on the server?**
The paragraph must be a non-empty string within the length limit, and the mode must be `standard` or
`safe`. The request body must be JSON. Malformed JSON returns 400; the wrong content type returns 415.

**28. How are secrets handled?**
No secrets are hardcoded. `.env` files are excluded by `.gitignore`, `.env.example` holds placeholders
only, and a pytest check guards the source files against accidental credential strings.

**29. What is the role of the test suite?**
It proves the behaviour is reproducible: 38 extraction tests, 36 validator tests, and 33 API tests,
107 in total, all passing.

**30. What would you improve next?**
Add an optional validated LLM adapter, support more event types, add batch extraction, and export to
CSV or a database. Any model output would be validated against the same schema before display.
