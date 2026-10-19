# Test Results

**Project:** Prompt-Based Information Extraction System
**Student:** Harshad Babulal Imale (MCA)
**Engine:** deterministic-rule-based v1.0 (no external AI API)

All results below were produced by actually running the project. Nothing in this document is estimated
or fabricated.

---

## 1. Automated pytest suite

**Command**

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

**Result**

```
============================= 107 passed in 0.48s =============================
```

| Test file | Tests | Status |
|---|---|---|
| `tests/test_extractor.py` | 38 | all passed |
| `tests/test_validator.py` | 36 | all passed |
| `tests/test_app.py` | 33 | all passed |
| **Total** | **107** | **all passed** |

### Full pytest output

<details>
<summary>Click to expand the recorded console output</summary>

```text
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.7.0 -- C:\Users\Admin\Documents\Default Project\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Admin\Documents\Default Project
configfile: pytest.ini
testpaths: tests
collecting ... collected 107 items

tests/test_app.py::test_index_page_renders PASSED                        [  0%]
tests/test_app.py::test_report_page_renders PASSED                       [  1%]
tests/test_app.py::test_unknown_page_returns_404_page PASSED             [  2%]
tests/test_app.py::test_health_endpoint PASSED                           [  3%]
tests/test_app.py::test_samples_endpoint PASSED                          [  4%]
tests/test_app.py::test_prompts_endpoint PASSED                          [  5%]
tests/test_app.py::test_extract_complete_paragraph PASSED                [  6%]
tests/test_app.py::test_extract_missing_information PASSED               [  7%]
tests/test_app.py::test_extract_sparse_safe_mode PASSED                  [  8%]
tests/test_app.py::test_extract_defaults_to_standard_mode PASSED         [  9%]
tests/test_app.py::test_extract_empty_paragraph_returns_400 PASSED       [ 10%]
tests/test_app.py::test_extract_missing_paragraph_field_returns_400 PASSED [ 11%]
tests/test_app.py::test_extract_unsupported_mode_returns_400 PASSED      [ 12%]
tests/test_app.py::test_extract_non_string_paragraph_returns_400 PASSED  [ 13%]
tests/test_app.py::test_extract_requires_json_content_type PASSED        [ 14%]
tests/test_app.py::test_extract_malformed_json_returns_400 PASSED        [ 14%]
tests/test_app.py::test_extract_json_array_body_returns_400 PASSED       [ 15%]
tests/test_app.py::test_extract_over_length_returns_400 PASSED           [ 16%]
tests/test_app.py::test_validate_valid_json_string PASSED                [ 17%]
tests/test_app.py::test_validate_accepts_object PASSED                   [ 18%]
tests/test_app.py::test_validate_invalid_json PASSED                     [ 19%]
tests/test_app.py::test_validate_missing_key PASSED                      [ 20%]
tests/test_app.py::test_validate_extra_key PASSED                        [ 21%]
tests/test_app.py::test_validate_invalid_date PASSED                     [ 22%]
tests/test_app.py::test_validate_missing_json_field_returns_400 PASSED   [ 23%]
tests/test_app.py::test_validate_empty_string_returns_400 PASSED         [ 24%]
tests/test_app.py::test_validate_wrong_type_returns_400 PASSED           [ 25%]
tests/test_app.py::test_run_tests_all_pass PASSED                        [ 26%]
tests/test_app.py::test_run_tests_field_level_details PASSED             [ 27%]
tests/test_app.py::test_unknown_api_endpoint_returns_json_404 PASSED     [ 28%]
tests/test_app.py::test_wrong_method_returns_405 PASSED                  [ 28%]
tests/test_app.py::test_payload_too_large_returns_413 PASSED             [ 29%]
tests/test_app.py::test_no_secrets_in_source PASSED                      [ 30%]
tests/test_extractor.py::test_complete_paragraph_all_fields PASSED       [ 31%]
tests/test_extractor.py::test_complete_paragraph_venue_includes_institute_and_city PASSED [ 32%]
tests/test_extractor.py::test_complete_paragraph_date_is_iso PASSED      [ 33%]
tests/test_extractor.py::test_missing_venue_and_speaker_are_null PASSED  [ 34%]
tests/test_extractor.py::test_sparse_paragraph_is_fully_null PASSED      [ 35%]
tests/test_extractor.py::test_sparse_paragraph_standard_mode_also_null PASSED [ 36%]
tests/test_extractor.py::test_no_workshop_details_paragraph PASSED       [ 37%]
tests/test_extractor.py::test_empty_paragraph_returns_schema[] PASSED    [ 38%]
tests/test_extractor.py::test_empty_paragraph_returns_schema[   ] PASSED [ 39%]
tests/test_extractor.py::test_empty_paragraph_returns_schema[\n\n\t] PASSED [ 40%]
tests/test_extractor.py::test_invalid_mode_raises PASSED                 [ 41%]
tests/test_extractor.py::test_valid_date_formats[The workshop is on 15 November 2026.-2026-11-15] PASSED [ 42%]
tests/test_extractor.py::test_valid_date_formats[The workshop is on November 15, 2026.-2026-11-15] PASSED [ 42%]
tests/test_extractor.py::test_valid_date_formats[The workshop is on 1st January 2027.-2027-01-01] PASSED [ 43%]
tests/test_extractor.py::test_valid_date_formats[The workshop is on 2026-11-15.-2026-11-15] PASSED [ 44%]
tests/test_extractor.py::test_valid_date_formats[The workshop is on 29 February 2028.-2028-02-29] PASSED [ 45%]
tests/test_extractor.py::test_ambiguous_or_invalid_dates_are_null[The workshop is on 31 February 2026.] PASSED [ 46%]
tests/test_extractor.py::test_ambiguous_or_invalid_dates_are_null[The workshop is on 15 November.] PASSED [ 47%]
tests/test_extractor.py::test_ambiguous_or_invalid_dates_are_null[The workshop is next month.] PASSED [ 48%]
tests/test_extractor.py::test_ambiguous_or_invalid_dates_are_null[The workshop is tomorrow.] PASSED [ 49%]
tests/test_extractor.py::test_ambiguous_or_invalid_dates_are_null[The workshop is on 03/04/2026.] PASSED [ 50%]
tests/test_extractor.py::test_date_evidence_recorded PASSED              [ 51%]
tests/test_extractor.py::test_title_normalised_for_missing_paragraph PASSED [ 52%]
tests/test_extractor.py::test_generic_title_rejected_in_safe_mode PASSED [ 53%]
tests/test_extractor.py::test_generic_title_fallback_in_standard_mode_requires_specificity PASSED [ 54%]
tests/test_extractor.py::test_title_not_expanded_with_unsupported_details PASSED [ 55%]
tests/test_extractor.py::test_speaker_extracted_with_honorific PASSED    [ 56%]
tests/test_extractor.py::test_role_only_speaker_is_null PASSED           [ 57%]
tests/test_extractor.py::test_unannounced_speaker_is_null PASSED         [ 57%]
tests/test_extractor.py::test_topics_split_on_commas_and_and PASSED      [ 58%]
tests/test_extractor.py::test_topics_are_deduplicated PASSED             [ 59%]
tests/test_extractor.py::test_no_topic_cue_gives_empty_array PASSED      [ 60%]
tests/test_extractor.py::test_output_always_has_exactly_five_keys PASSED [ 61%]
tests/test_extractor.py::test_output_is_json_serialisable PASSED         [ 62%]
tests/test_extractor.py::test_meta_reports_engine_honestly PASSED        [ 63%]
tests/test_extractor.py::test_notes_explain_missing_fields PASSED        [ 64%]
tests/test_extractor.py::test_labelled_input_is_supported PASSED         [ 65%]
tests/test_extractor.py::test_long_paragraph_does_not_crash PASSED       [ 66%]
tests/test_validator.py::test_valid_complete_record_passes PASSED        [ 67%]
tests/test_validator.py::test_valid_missing_record_passes PASSED         [ 68%]
tests/test_validator.py::test_valid_sparse_record_passes PASSED          [ 69%]
tests/test_validator.py::test_invalid_json_syntax_is_reported PASSED     [ 70%]
tests/test_validator.py::test_empty_json_is_invalid PASSED               [ 71%]
tests/test_validator.py::test_syntax_and_schema_are_separate PASSED      [ 71%]
tests/test_validator.py::test_root_must_be_object PASSED                 [ 72%]
tests/test_validator.py::test_missing_required_key_is_detected PASSED    [ 73%]
tests/test_validator.py::test_extra_key_is_detected PASSED               [ 74%]
tests/test_validator.py::test_each_required_key_is_enforced[title] PASSED [ 75%]
tests/test_validator.py::test_each_required_key_is_enforced[date] PASSED [ 76%]
tests/test_validator.py::test_each_required_key_is_enforced[venue] PASSED [ 77%]
tests/test_validator.py::test_each_required_key_is_enforced[speaker] PASSED [ 78%]
tests/test_validator.py::test_each_required_key_is_enforced[topics] PASSED [ 79%]
tests/test_validator.py::test_wrong_scalar_type_is_detected PASSED       [ 80%]
tests/test_validator.py::test_topics_must_be_array PASSED                [ 81%]
tests/test_validator.py::test_topics_must_contain_only_strings PASSED    [ 82%]
tests/test_validator.py::test_topics_rejects_empty_string PASSED         [ 83%]
tests/test_validator.py::test_empty_string_scalar_is_rejected PASSED     [ 84%]
tests/test_validator.py::test_null_substitute_strings_are_rejected[null] PASSED [ 85%]
tests/test_validator.py::test_null_substitute_strings_are_rejected[N/A] PASSED [ 85%]
tests/test_validator.py::test_null_substitute_strings_are_rejected[Unknown] PASSED [ 86%]
tests/test_validator.py::test_null_substitute_strings_are_rejected[None] PASSED [ 87%]
tests/test_validator.py::test_null_substitute_strings_are_rejected[-] PASSED [ 88%]
tests/test_validator.py::test_actual_json_null_is_accepted PASSED        [ 89%]
tests/test_validator.py::test_invalid_date_formats_are_rejected[15-11-2026] PASSED [ 90%]
tests/test_validator.py::test_invalid_date_formats_are_rejected[2026/11/15] PASSED [ 91%]
tests/test_validator.py::test_invalid_date_formats_are_rejected[2026-13-01] PASSED [ 92%]
tests/test_validator.py::test_invalid_date_formats_are_rejected[2026-02-30] PASSED [ 93%]
tests/test_validator.py::test_invalid_date_formats_are_rejected[15 November 2026] PASSED [ 94%]
tests/test_validator.py::test_invalid_date_formats_are_rejected[2026-1-5] PASSED [ 95%]
tests/test_validator.py::test_null_date_is_accepted PASSED               [ 96%]
tests/test_validator.py::test_leap_day_is_accepted PASSED                [ 97%]
tests/test_validator.py::test_checks_are_reported_individually PASSED    [ 98%]
tests/test_validator.py::test_report_is_json_serialisable PASSED         [ 99%]
tests/test_validator.py::test_oversized_json_is_rejected PASSED          [100%]

============================= 107 passed in 0.48s =============================
```

</details>

---

## 2. Built-in scenario runner (`POST /api/tests/run`)

The web application can run the three required scenarios from the **Test Suite** tab. The runner uses
the same engine and validator as the application, checks JSON syntax, validates the schema, and
compares every field with its documented expected value.

**Summary: 3 of 3 scenarios passed.**

### TEST 1 - Complete Information

**Prompt mode:** `standard` (Standard Extraction)

**Input paragraph**

> DKTE Society's Textile & Engineering Institute, Ichalkaranji, will organize the Introduction to Generative AI and Prompt Engineering Workshop on 15 November 2026 in the Seminar Hall. Dr. Ananya Deshmukh will be the speaker. The workshop will cover Prompt Design, Structured JSON Output, Context Engineering, and AI Output Validation.

**Extracted JSON**

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

**JSON syntax validation:** PASS  
**Schema validation:** PASS  
**Overall:** PASS

| Field | Expected | Actual | Match |
|---|---|---|---|
| `title` | "Introduction to Generative AI and Prompt Engineering Workshop" | "Introduction to Generative AI and Prompt Engineering Workshop" | yes |
| `date` | "2026-11-15" | "2026-11-15" | yes |
| `venue` | "Seminar Hall, DKTE Society's Textile & Engineering Institute, Ichalkaranji" | "Seminar Hall, DKTE Society's Textile & Engineering Institute, Ichalkaranji" | yes |
| `speaker` | "Dr. Ananya Deshmukh" | "Dr. Ananya Deshmukh" | yes |
| `topics` | ["Prompt Design", "Structured JSON Output", "Context Engineering", "AI Output Validation"] | ["Prompt Design", "Structured JSON Output", "Context Engineering", "AI Output Validation"] | yes |

### TEST 2 - Missing Information

**Prompt mode:** `standard` (Standard Extraction)

**Input paragraph**

> The college will conduct a Python programming workshop on 20 December 2026. Students will learn file handling and exception handling.

**Extracted JSON**

```json
{
  "title": "Python programming workshop",
  "date": "2026-12-20",
  "venue": null,
  "speaker": null,
  "topics": [
    "file handling",
    "exception handling"
  ]
}
```

**JSON syntax validation:** PASS  
**Schema validation:** PASS  
**Overall:** PASS

| Field | Expected | Actual | Match |
|---|---|---|---|
| `title` | "Python programming workshop" | "Python programming workshop" | yes |
| `date` | "2026-12-20" | "2026-12-20" | yes |
| `venue` | null | null | yes |
| `speaker` | null | null | yes |
| `topics` | ["file handling", "exception handling"] | ["file handling", "exception handling"] | yes |

**Missing-information notes**

- No explicit venue phrase (for example 'in the Seminar Hall' or 'at the Auditorium') was found. A host institution name alone is not converted into a venue.
- No speaker name was supplied. Role-only references such as 'the speaker' are not treated as names, and no name is invented.

### TEST 3 - Sparse / Ambiguous Information

**Prompt mode:** `safe` (Missing-Information-Safe Extraction)

**Input paragraph**

> A technical workshop will be organized next month. The speaker has not been announced.

**Extracted JSON**

```json
{
  "title": null,
  "date": null,
  "venue": null,
  "speaker": null,
  "topics": []
}
```

**JSON syntax validation:** PASS  
**Schema validation:** PASS  
**Overall:** PASS

| Field | Expected | Actual | Match |
|---|---|---|---|
| `title` | null | null | yes |
| `date` | null | null | yes |
| `venue` | null | null | yes |
| `speaker` | null | null | yes |
| `topics` | [] | [] | yes |

**Missing-information notes**

- No specific event title was found. Generic descriptions such as 'technical workshop' are not treated as titles, and the title is not invented.
- The paragraph gives a relative or ambiguous time reference, not a full calendar date.
- No explicit venue phrase (for example 'in the Seminar Hall' or 'at the Auditorium') was found. A host institution name alone is not converted into a venue.
- No speaker name was supplied. Role-only references such as 'the speaker' are not treated as names, and no name is invented.
- No explicit topic list cue (for example 'will cover' or 'topics include') was found, so topics is an empty array.


---

## 3. What the tests prove

| Requirement | Evidence |
|---|---|
| Complete information is extracted | TEST 1 matches all five expected fields |
| Missing venue and speaker become null | TEST 2 returns `null` for both and explains why |
| Sparse input does not create facts | TEST 3 returns all null / `[]` |
| Syntax and schema validated separately | Validator reports two independent layers |
| Invalid JSON detected | `test_invalid_json_syntax_is_reported` |
| Missing key detected | `test_missing_required_key_is_detected` |
| Extra key detected | `test_extra_key_is_detected` |
| Wrong data type detected | `test_wrong_scalar_type_is_detected`, `test_topics_must_contain_only_strings` |
| Invalid date detected | `test_invalid_date_formats_are_rejected` |
| Malformed API requests handled | `test_extract_malformed_json_returns_400`, `test_extract_json_array_body_returns_400` |
| Health endpoint works | `test_health_endpoint` |

---

## 4. Reproducing these results

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -v
```

Then start the application and use **Run All Tests** in the Test Suite tab:

```powershell
.\.venv\Scripts\python.exe app.py
```
