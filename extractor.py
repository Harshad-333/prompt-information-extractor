"""Deterministic, rule-based information extraction for workshop paragraphs.

This module is intentionally transparent. It uses sentence splitting, regular
expressions, a small date parser, and explicit cue phrases. It does **not** call
a language model and does not require an API key.

Design principles
-----------------
1. Extract only what is explicitly present.
2. Never guess a speaker, venue, or calendar date.
3. Return the required five-field dictionary with ``None`` / ``[]`` for missing
   information.
4. Record evidence and human-readable notes so the UI can explain *why* a field
   is null.

The two prompt modes share one parser. The mode only changes how strict the
title fallback is; both modes obey the same "no invention" contract.
"""

from __future__ import annotations

import re
from datetime import date as _date
from typing import Any, Dict, List, Optional, Tuple

ENGINE_NAME = "deterministic-rule-based"
ENGINE_VERSION = "1.0"

# ---------------------------------------------------------------------------
# Vocabulary
# ---------------------------------------------------------------------------

MONTHS = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}

MONTH_PATTERN = "|".join(sorted(MONTHS, key=len, reverse=True))

EVENT_WORDS = (
    "workshop|seminar|webinar|conference|symposium|colloquium|bootcamp|"
    "boot camp|training programme|training program|faculty development programme|"
    "faculty development program|fdp|guest lecture|lecture|session|programme|program"
)
EVENT_RE = re.compile(rf"\b(?:{EVENT_WORDS})\b", re.IGNORECASE)

VENUE_WORDS = (
    "Seminar Hall|Conference Hall|Auditorium|Lecture Hall|Seminar Room|"
    "Conference Room|Computer Lab|Computer Laboratory|Laboratory|Lab|"
    "Convention Centre|Convention Center|Auditorium Hall|Open Ground|Grounds|"
    "Theatre|Theater|Complex|Building|Block|Campus|Centre|Center|"
    "Institute|College|University|Hotel"
)
VENUE_WORD_RE = re.compile(rf"\b(?:{VENUE_WORDS})\b", re.IGNORECASE)

HONORIFICS = r"(?:Dr|Prof|Professor|Mr|Mrs|Ms|Mx|Shri|Smt)"
NAME_TOKEN = r"[A-Z][A-Za-z\u2019'.\-]+"
NAME_RE = rf"{NAME_TOKEN}(?:\s+{NAME_TOKEN}){{0,3}}"

GENERIC_TITLE_WORDS = {
    "a", "an", "the", "this", "that", "these", "those", "our", "their",
    "technical", "national", "international", "annual", "online", "offline",
    "one", "two", "three", "day", "days", "week", "month", "upcoming",
    "special", "guest", "basic", "advanced", "introductory", "general",
    "workshop", "workshops", "seminar", "webinar", "conference", "symposium",
    "colloquium", "bootcamp", "boot", "camp", "training", "programme", "program",
    "session", "lecture", "talk", "fdp", "college", "students", "faculty",
    "department", "school", "institute", "university", "event", "program",
    "and", "or", "of", "for", "on", "in", "at", "to", "with", "by", "from",
    "will", "be", "is", "are", "was", "were", "has", "have", "had",
}

STOPWORDS = {
    "a", "an", "the", "of", "for", "on", "in", "at", "to", "with", "by",
    "from", "and", "or", "is", "are", "was", "were", "will", "be", "been",
    "this", "that", "these", "those", "it", "its", "as", "via",
}

ABBREVIATIONS = ["Dr.", "Prof.", "Mr.", "Mrs.", "Ms.", "Mx.", "Shri.", "Smt.",
                 "vs.", "etc.", "e.g.", "i.e.", "St."]


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _clean_text(text: str) -> str:
    """Normalise whitespace and common typographic characters."""
    text = str(text).replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _sentences(text: str) -> List[str]:
    """Split into sentences while protecting common abbreviations."""
    protected = text
    replacements: List[Tuple[str, str]] = []
    for index, abbreviation in enumerate(ABBREVIATIONS):
        token = f"\x00ABBR{index}\x00"
        replacements.append((token, abbreviation))
        protected = re.sub(re.escape(abbreviation), token, protected, flags=re.IGNORECASE)

    parts = re.split(r"(?<=[.!?])\s+|\n+", protected)
    result: List[str] = []
    for part in parts:
        restored = part
        for token, abbreviation in replacements:
            restored = restored.replace(token, abbreviation)
        restored = restored.strip()
        if restored:
            result.append(restored)
    return result


def _sentence_for(text: str, span: Tuple[int, int]) -> str:
    """Return the sentence containing a character span (best effort)."""
    start, end = span
    before = text[:start]
    after = text[end:]
    left = max(before.rfind("."), before.rfind("!"), before.rfind("?"), before.rfind("\n"))
    right_candidates = [i for i in (after.find("."), after.find("!"), after.find("?"), after.find("\n")) if i != -1]
    right = min(right_candidates) if right_candidates else len(after)
    return text[left + 1: end + right + 1].strip()


def _strip_article(value: str) -> str:
    return re.sub(r"^(?:the|a|an)\s+", "", value.strip(), flags=re.IGNORECASE).strip()


def _normalise_phrase(value: str) -> str:
    value = value.strip().strip("\"'“”‘’")
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" ,;:-")
    return value.strip()


def _content_words(value: str) -> List[str]:
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", value)
    return [w for w in words if w.lower() not in STOPWORDS and w.lower() not in GENERIC_TITLE_WORDS]


def _has_proper_noun(value: str) -> bool:
    """True when a candidate has a capitalised word that is not generic."""
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", value)
    for word in words:
        if not word[0].isupper():
            continue
        lower = word.lower()
        if lower in GENERIC_TITLE_WORDS or lower in STOPWORDS:
            continue
        if word.isupper() and len(word) >= 2:  # acronyms such as AI, JSON
            return True
        return True
    return False


def _title_is_specific(candidate: str, mode: str) -> bool:
    """Apply documented title-specificity rules for the selected mode."""
    if not candidate:
        return False
    if len(candidate) < 4 or len(candidate) > 140:
        return False
    if not EVENT_RE.search(candidate):
        return False
    if re.search(r"\b(?:next|last|this)\s+(?:week|month|year)\b", candidate, re.IGNORECASE):
        return False
    if re.search(r"\b(?:will|shall|would|should|is|are|was|were|has|have|had)\b", candidate, re.IGNORECASE):
        return False
    if _has_proper_noun(candidate):
        return True
    # Standard mode has a documented fallback: a descriptive phrase with at least
    # two non-generic content words (for example "workshop on data science").
    # Safe mode never accepts a title without a proper noun.
    if mode == "standard" and len(_content_words(candidate)) >= 2:
        return True
    return False


# ---------------------------------------------------------------------------
# Date extraction
# ---------------------------------------------------------------------------

def _valid_iso(year: int, month: int, day: int) -> Optional[str]:
    try:
        return _date(year, month, day).isoformat()
    except ValueError:
        return None


def extract_date(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Return ``(iso_date, evidence, note)``.

    ``iso_date`` is None for missing, relative, partial, or ambiguous dates.
    """
    iso_match = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", text)
    if iso_match:
        iso = _valid_iso(int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3)))
        if iso:
            return iso, iso_match.group(0), None
        return None, iso_match.group(0), "The date is not a valid calendar date, so it was kept as null."

    day_month_year = re.search(
        rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+(?:of\s+)?({MONTH_PATTERN})\s*,?\s+(\d{{4}})\b",
        text, re.IGNORECASE,
    )
    if day_month_year:
        day = int(day_month_year.group(1))
        month = MONTHS[day_month_year.group(2).lower()]
        year = int(day_month_year.group(3))
        iso = _valid_iso(year, month, day)
        if iso:
            return iso, day_month_year.group(0), None
        return None, day_month_year.group(0), "The date is not a valid calendar date, so it was kept as null."

    month_day_year = re.search(
        rf"\b({MONTH_PATTERN})\s+(\d{{1,2}})(?:st|nd|rd|th)?\s*,?\s+(\d{{4}})\b",
        text, re.IGNORECASE,
    )
    if month_day_year:
        month = MONTHS[month_day_year.group(1).lower()]
        day = int(month_day_year.group(2))
        year = int(month_day_year.group(3))
        iso = _valid_iso(year, month, day)
        if iso:
            return iso, month_day_year.group(0), None
        return None, month_day_year.group(0), "The date is not a valid calendar date, so it was kept as null."

    numeric = re.search(r"\b(\d{1,2})[/.](\d{1,2})[/.](\d{2,4})\b", text)
    if numeric:
        return (
            None,
            numeric.group(0),
            "A numeric date such as this is ambiguous (day/month vs month/day), "
            "so it was not converted into a specific calendar date.",
        )

    relative = re.search(
        r"\b(?:today|tomorrow|yesterday|next|last|this)\s+(?:week|month|year|monday|tuesday|wednesday|"
        r"thursday|friday|saturday|sunday)\b|\bsoon\b|\bshortly\b",
        text, re.IGNORECASE,
    )
    if relative:
        return (
            None,
            relative.group(0),
            "The paragraph gives a relative or ambiguous time reference, not a full calendar date.",
        )

    partial = re.search(rf"\b(?:{MONTH_PATTERN})\s+\d{{4}}\b", text, re.IGNORECASE)
    if partial:
        return (
            None,
            partial.group(0),
            "A month and year were supplied without a day, so a complete ISO date cannot be formed.",
        )

    return None, None, "No full calendar date was stated in the paragraph."


# ---------------------------------------------------------------------------
# Title extraction
# ---------------------------------------------------------------------------

def _candidate_after_verb(text: str) -> Optional[Tuple[str, int, int]]:
    verb = (
        r"(?:organi[sz](?:e|es|ed|ing)|conduct(?:s|ed|ing)?|host(?:s|ed|ing)?|"
        r"hold(?:s|ing)?|arrang(?:e|es|ed|ing)|present(?:s|ed|ing)?|deliver(?:s|ed|ing)?)"
    )
    pattern = re.compile(
        rf"\b(?:will\s+(?:be\s+)?|is\s+|are\s+|shall\s+)?{verb}\s+(?:the|a|an)\s+"
        rf"(?P<title>[^.;]{{3,140}}?)(?=\s+(?:on|from)\s+|\s*[.;]|$)",
        re.IGNORECASE,
    )
    match = pattern.search(text)
    if not match:
        return None
    return _normalise_phrase(match.group("title")), match.start("title"), match.end("title")


def _candidate_event_on_topic(text: str) -> Optional[Tuple[str, int, int]]:
    """Match headline style titles such as 'Workshop on Cyber Security'."""
    pattern = re.compile(
        rf"\b(?P<title>(?:[A-Z][A-Za-z0-9&'\-]*\s+){{0,4}}(?:{EVENT_WORDS})"
        rf"\s+on\s+[A-Z][A-Za-z0-9&'\-]*(?:\s+[A-Za-z0-9&'\-]+){{0,4}})",
        re.IGNORECASE,
    )
    match = pattern.search(text)
    if not match:
        return None
    title = _normalise_phrase(match.group("title"))
    if title and title[0].islower():
        title = title[0].upper() + title[1:]
    return title, match.start("title"), match.end("title")


def _candidate_before_verb(text: str) -> Optional[Tuple[str, int, int]]:
    pattern = re.compile(
        r"\b(?:the|a|an)\s+(?P<title>[^.;]{3,140}?)\s+"
        r"(?:will\s+be\s+|is\s+|are\s+|was\s+|were\s+)?"
        r"(?:organi[sz]ed|conducted|held|hosted|arranged)\b",
        re.IGNORECASE,
    )
    match = pattern.search(text)
    if not match:
        return None
    title = _trim_title_tail(_normalise_phrase(match.group("title")))
    if not EVENT_RE.search(title):
        return None
    return title, match.start("title"), match.end("title")


def _trim_title_tail(candidate: str) -> str:
    """Remove trailing date, venue, or speaker clauses that are not part of the title."""
    candidate = re.sub(
        rf"\s+(?:in|at)\s+(?:the\s+)?(?:{VENUE_WORDS})\b.*$", "", candidate, flags=re.IGNORECASE
    )
    candidate = re.sub(
        rf"\s+(?:on|at)\s+(?:\d|(?:{MONTH_PATTERN})\b).*$", "", candidate, flags=re.IGNORECASE
    )
    candidate = re.sub(
        r"\s+(?:on|at)\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b.*$",
        "", candidate, flags=re.IGNORECASE,
    )
    # Headline lists often append comma-separated date / venue / speaker fragments.
    candidate = re.split(r"\s*,\s*", candidate)[0]
    return _normalise_phrase(candidate)


def _candidate_by_event_phrase(sentence: str) -> Optional[Tuple[str, int, int]]:
    match = EVENT_RE.search(sentence)
    if not match:
        return None
    prefix = sentence[: match.end()]
    prefix = re.split(r"[,;:]", prefix)[-1]
    candidate = _normalise_phrase(prefix)
    candidate = _strip_article(candidate)
    if not candidate:
        return None
    return candidate, 0, match.end()


def extract_title(text: str, mode: str, labelled: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str], str]:
    """Return ``(title, evidence, note, confidence)``."""
    if labelled:
        candidate = _strip_article(_normalise_phrase(labelled))
        if _title_is_specific(candidate, mode):
            return candidate, f"Title label: {labelled}", None, "high"
        return None, f"Title label: {labelled}", (
            "The supplied title label was empty or too generic to treat as a specific event title."
        ), "none"

    candidates: List[Tuple[str, int, int, str]] = []
    for finder, confidence in (
        (_candidate_after_verb, "high"),
        (_candidate_event_on_topic, "high"),
        (_candidate_before_verb, "medium"),
    ):
        found = finder(text)
        if found:
            candidates.append((found[0], found[1], found[2], confidence))

    for sentence in _sentences(text):
        if EVENT_RE.search(sentence):
            found = _candidate_by_event_phrase(sentence)
            if found:
                candidates.append((found[0], found[1], found[2], "low"))
            break

    for candidate, start, end, confidence in candidates:
        candidate = _trim_title_tail(candidate)
        if _title_is_specific(candidate, mode):
            evidence = _sentence_for(text, (start, end)) or candidate
            return candidate, evidence, None, confidence

    return None, None, (
        "No specific event title was found. Generic descriptions such as "
        "'technical workshop' are not treated as titles, and the title is not invented."
    ), "none"


# ---------------------------------------------------------------------------
# Venue extraction
# ---------------------------------------------------------------------------

def _explicit_venue(text: str) -> Optional[Tuple[str, int, int]]:
    pattern = re.compile(
        rf"\b(?:in|at)\s+(?:the\s+)?(?P<venue>(?:[A-Z][A-Za-z0-9&'.\-]*\s*){{0,8}}?(?:{VENUE_WORDS}))\b",
        re.IGNORECASE,
    )
    match = pattern.search(text)
    if not match:
        return None
    venue = _normalise_phrase(match.group("venue"))
    if not venue:
        return None
    # A bare generic noun is not a venue name.
    if venue.lower() in {"college", "institute", "university", "campus", "building", "block", "lab"}:
        return None
    return venue, match.start("venue"), match.end("venue")


def _host_institution(text: str) -> Optional[Tuple[str, str]]:
    pattern = re.compile(
        r"\b(?P<host>[A-Z][A-Za-z0-9&'.\- ]{2,120}?(?:Institute|College|University|Department|School|Academy))"
        r"\s*,\s*(?P<city>[A-Z][A-Za-z.'\-]+(?:\s+[A-Z][A-Za-z.'\-]+){0,2})"
        r"\s*,?\s*(?:will|is|are|shall)\b",
        re.IGNORECASE,
    )
    match = pattern.search(text)
    if not match:
        return None
    host = _normalise_phrase(match.group("host"))
    city = _normalise_phrase(match.group("city"))
    if not host:
        return None
    return host, city


def extract_venue(text: str, labelled: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str], str]:
    """Return ``(venue, evidence, note, confidence)``."""
    if labelled:
        venue = _normalise_phrase(labelled)
        if venue:
            return venue, f"Venue label: {labelled}", None, "high"
        return None, f"Venue label: {labelled}", "The venue label was empty, so venue is null.", "none"

    explicit = _explicit_venue(text)
    if explicit:
        venue, start, end = explicit
        host = _host_institution(text)
        if host:
            host_name, city = host
            if host_name.lower() not in venue.lower() and venue.lower() not in host_name.lower():
                venue = f"{venue}, {host_name}"
                if city and city.lower() not in host_name.lower():
                    venue += f", {city}"
        return venue, _sentence_for(text, (start, end)) or venue, None, "high"

    return None, None, (
        "No explicit venue phrase (for example 'in the Seminar Hall' or 'at the Auditorium') "
        "was found. A host institution name alone is not converted into a venue."
    ), "none"


# ---------------------------------------------------------------------------
# Speaker extraction
# ---------------------------------------------------------------------------

def extract_speaker(text: str, labelled: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str], str]:
    """Return ``(speaker, evidence, note, confidence)``."""
    if labelled:
        speaker = _normalise_phrase(labelled)
        if speaker and not _looks_unannounced(speaker):
            return speaker, f"Speaker label: {labelled}", None, "high"
        return None, f"Speaker label: {labelled}", (
            "The speaker label was empty, a role, or marked as not announced, so speaker is null."
        ), "none"

    if _looks_unannounced(text):
        return None, None, (
            "The paragraph explicitly says the speaker is not announced, so no name is invented."
        ), "none"

    patterns = [
        re.compile(
            rf"\b(?P<name>{HONORIFICS}\.?\s+{NAME_RE})\s+"
            rf"(?:will\s+be|is|was|will\s+deliver|will\s+speak|will\s+present|will\s+address)\b"
        ),
        re.compile(
            rf"\b(?:speaker|resource\s+person|presenter)\s*(?:will\s+be|is|was|:)\s*"
            rf"(?P<name>{HONORIFICS}\.?\s+{NAME_RE})\b",
            re.IGNORECASE,
        ),
        re.compile(
            rf"\b(?P<name>{NAME_TOKEN}(?:\s+{NAME_TOKEN}){{1,3}})\s+will\s+be\s+the\s+speaker\b"
        ),
    ]

    for pattern in patterns:
        match = pattern.search(text)
        if not match:
            continue
        name = _normalise_phrase(match.group("name"))
        if not name or _looks_unannounced(name):
            continue
        if re.search(rf"\b(?:{EVENT_WORDS})\b", name, re.IGNORECASE):
            continue
        if name.lower() in {"the speaker", "speaker", "resource person"}:
            continue
        confidence = "high" if re.match(HONORIFICS, name) else "medium"
        return name, _sentence_for(text, match.span()), None, confidence

    return None, None, (
        "No speaker name was supplied. Role-only references such as 'the speaker' "
        "are not treated as names, and no name is invented."
    ), "none"


def _looks_unannounced(text: str) -> bool:
    return bool(re.search(
        r"\b(?:not\s+(?:yet\s+)?announced|to\s+be\s+announced|will\s+be\s+announced|"
        r"tba|tbd|to\s+be\s+confirmed|not\s+confirmed|yet\s+to\s+be\s+finali[sz]ed)\b",
        text, re.IGNORECASE,
    ))


# ---------------------------------------------------------------------------
# Topic extraction
# ---------------------------------------------------------------------------

TOPIC_CUE_RE = re.compile(
    r"\b(?:will\s+cover|will\s+include|will\s+explore|will\s+discuss|will\s+focus\s+on|"
    r"will\s+learn|will\s+teach|will\s+introduce|topics?\s+(?:include|are|will\s+be)|"
    r"covers|includes|focuses\s+on|focus\s+on|sessions?\s+on|contents?\s+(?:include|are))\b",
    re.IGNORECASE,
)


def _split_topics(raw: str) -> List[str]:
    raw = raw.strip().rstrip(".").strip()
    raw = re.sub(r"^(?:the\s+following\s+)?topics?\s*[:\-]\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r",\s*and\s+", ", ", raw)
    raw = re.sub(r"\s+and\s+", " and ", raw)
    if "," in raw or ";" in raw:
        parts = re.split(r"\s*[,;]\s*", raw)
    else:
        parts = re.split(r"\s+and\s+", raw)

    topics: List[str] = []
    seen = set()
    for part in parts:
        topic = _normalise_phrase(part)
        topic = re.sub(r"^(?:and|also)\s+", "", topic, flags=re.IGNORECASE)
        topic = topic.strip(" .")
        if not topic:
            continue
        if topic.lower() in {"etc", "etc.", "more", "other topics", "others"}:
            continue
        if len(topic) < 2 or len(topic) > 100:
            continue
        key = topic.lower()
        if key in seen:
            continue
        seen.add(key)
        topics.append(topic)
        if len(topics) >= 20:
            break
    return topics


def extract_topics(text: str, labelled: Optional[str]) -> Tuple[List[str], Optional[str], Optional[str], str]:
    """Return ``(topics, evidence, note, confidence)``."""
    if labelled:
        topics = _split_topics(labelled)
        if topics:
            return topics, f"Topics label: {labelled}", None, "high"
        return [], f"Topics label: {labelled}", "The topics label contained no usable topic strings.", "none"

    for sentence in _sentences(text):
        match = TOPIC_CUE_RE.search(sentence)
        if not match:
            continue
        raw = sentence[match.end():].strip()
        topics = _split_topics(raw)
        if topics:
            return topics, sentence, None, "high"

    return [], None, (
        "No explicit topic list cue (for example 'will cover' or 'topics include') "
        "was found, so topics is an empty array."
    ), "none"


# ---------------------------------------------------------------------------
# Labelled-field input
# ---------------------------------------------------------------------------

def _labelled_fields(text: str) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    aliases = {
        "title": "title", "event": "title", "event title": "title",
        "date": "date", "venue": "venue", "location": "venue",
        "speaker": "speaker", "resource person": "speaker", "presenter": "speaker",
        "topic": "topics", "topics": "topics",
    }
    for line in text.splitlines():
        match = re.match(r"^\s*([A-Za-z ]{2,20})\s*[:\-]\s*(.+?)\s*$", line)
        if not match:
            continue
        key = match.group(1).strip().lower()
        if key in aliases and aliases[key] not in fields:
            fields[aliases[key]] = match.group(2).strip()
    return fields


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract(paragraph: str, mode: str = "standard") -> Dict[str, Any]:
    """Extract structured information from *paragraph*.

    Returns a dictionary with ``data`` (the five schema fields) and ``meta``
    (mode, evidence, notes, confidence, warnings). The function never raises for
    ordinary text; invalid mode raises ``ValueError``.
    """
    if mode not in {"standard", "safe"}:
        raise ValueError("mode must be 'standard' or 'safe'")

    text = _clean_text(paragraph)
    labelled = _labelled_fields(text)

    title, title_evidence, title_note, title_conf = extract_title(text, mode, labelled.get("title"))
    date_value, date_evidence, date_note = extract_date(labelled.get("date") or text)
    venue, venue_evidence, venue_note, venue_conf = extract_venue(text, labelled.get("venue"))
    speaker, speaker_evidence, speaker_note, speaker_conf = extract_speaker(text, labelled.get("speaker"))
    topics, topics_evidence, topics_note, topics_conf = extract_topics(text, labelled.get("topics"))

    notes = [note for note in (title_note, date_note, venue_note, speaker_note, topics_note) if note]
    warnings: List[str] = []
    if not text:
        notes = ["The input paragraph is empty, so every field is null or an empty array."]
    if len(text) > 5000:
        warnings.append("The paragraph is longer than the recommended 5,000 characters.")

    data = {
        "title": title,
        "date": date_value,
        "venue": venue,
        "speaker": speaker,
        "topics": topics,
    }

    return {
        "data": data,
        "meta": {
            "engine": ENGINE_NAME,
            "engine_version": ENGINE_VERSION,
            "mode": mode,
            "mode_name": "Standard Extraction" if mode == "standard" else "Missing-Information-Safe Extraction",
            "confidence": {
                "title": title_conf,
                "date": "high" if date_value else "none",
                "venue": venue_conf,
                "speaker": speaker_conf,
                "topics": topics_conf,
            },
            "evidence": {
                "title": title_evidence,
                "date": date_evidence,
                "venue": venue_evidence,
                "speaker": speaker_evidence,
                "topics": topics_evidence,
            },
            "notes": notes,
            "warnings": warnings,
        },
    }


def extract_data(paragraph: str, mode: str = "standard") -> Dict[str, Any]:
    """Convenience wrapper returning only the five-field dictionary."""
    return extract(paragraph, mode)["data"]
