from __future__ import annotations

from difflib import SequenceMatcher
import re
import unicodedata

from llm_eval.extraction import as_decimal, normalize_answer


def answer_correct(expected: str, extracted: str, expected_regex: str | None = None) -> bool:
    if expected_regex and regex_matches(expected_regex, extracted):
        return True
    expected_norm = normalize_answer(expected)
    extracted_norm = normalize_answer(extracted)
    if expected_norm == extracted_norm:
        return True
    expected_num = as_decimal(expected)
    extracted_num = as_decimal(extracted)
    return expected_num is not None and extracted_num is not None and expected_num == extracted_num


def response_correct(
    expected: str,
    extracted: str,
    raw_response: str,
    expected_regex: str | None = None,
) -> bool:
    if answer_correct(expected, extracted, expected_regex):
        return True
    if expected_regex and regex_matches(expected_regex, raw_response):
        return True
    expected_norm = normalize_answer(expected)
    raw_norm = normalize_answer(raw_response)
    if len(expected_norm) >= 3 and expected_norm in raw_norm:
        return True
    return semantic_match(expected, raw_response) or semantic_match(expected, extracted)


def semantic_match(expected: str | None, candidate: str | None) -> bool:
    expected_key = match_key(expected)
    candidate_key = match_key(candidate)
    if not expected_key or not candidate_key:
        return False
    if len(expected_key) >= 3 and expected_key in candidate_key:
        return True

    expected_tokens = content_tokens(expected_key)
    candidate_tokens = content_tokens(candidate_key)
    if not expected_tokens or not candidate_tokens:
        return False

    matched = sum(1 for token in expected_tokens if token_in(token, candidate_tokens))
    coverage = matched / len(expected_tokens)
    if len(expected_tokens) <= 3:
        return coverage >= 0.8
    if coverage >= 0.7:
        return True

    common_run = longest_common_token_run(expected_tokens, candidate_tokens)
    if common_run >= 3 and coverage >= 0.45:
        return True
    weighted_coverage = weighted_token_coverage(expected_tokens, candidate_tokens)
    if len(expected_tokens) >= 8 and matched >= 5 and coverage >= 0.5:
        return True
    return len(expected_tokens) >= 8 and matched >= 4 and weighted_coverage >= 0.4


def match_key(value: str | None) -> str:
    if value is None:
        return ""
    value = strip_accents(str(value).lower().replace("ς", "σ"))
    value = transliterate_greek(value)
    value = re.sub(r"final_answer\s*:", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def strip_accents(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value)
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def transliterate_greek(value: str) -> str:
    digraphs = (
        ("αι", "ai"),
        ("ει", "ei"),
        ("οι", "oi"),
        ("ου", "ou"),
        ("υι", "yi"),
        ("αυ", "au"),
        ("ευ", "eu"),
        ("ηυ", "iu"),
        ("μπ", "mp"),
        ("ντ", "nt"),
        ("γκ", "gk"),
        ("γγ", "ng"),
        ("τσ", "ts"),
        ("τζ", "tz"),
    )
    for greek, latin in digraphs:
        value = value.replace(greek, latin)
    return value.translate(
        str.maketrans(
            {
                "α": "a",
                "β": "v",
                "γ": "g",
                "δ": "d",
                "ε": "e",
                "ζ": "z",
                "η": "i",
                "θ": "th",
                "ι": "i",
                "κ": "k",
                "λ": "l",
                "μ": "m",
                "ν": "n",
                "ξ": "x",
                "ο": "o",
                "π": "p",
                "ρ": "r",
                "σ": "s",
                "τ": "t",
                "υ": "y",
                "φ": "f",
                "χ": "x",
                "ψ": "ps",
                "ω": "o",
            }
        )
    )


STOPWORDS = {
    "a",
    "an",
    "and",
    "alla",
    "apo",
    "auto",
    "auti",
    "autos",
    "den",
    "einai",
    "ena",
    "gia",
    "i",
    "kai",
    "k",
    "me",
    "mou",
    "na",
    "o",
    "oi",
    "oti",
    "pou",
    "se",
    "sou",
    "sto",
    "sta",
    "sti",
    "stin",
    "stis",
    "ta",
    "tha",
    "the",
    "tin",
    "tis",
    "to",
    "ton",
    "tou",
    "tous",
}


def content_tokens(value: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", value)
    return [token for token in tokens if token.isdigit() or (len(token) > 1 and token not in STOPWORDS)]


def token_in(token: str, candidates: list[str]) -> bool:
    return any(tokens_close(token, candidate) for candidate in candidates)


def tokens_close(left: str, right: str) -> bool:
    left_key = canonical_token(left)
    right_key = canonical_token(right)
    if left_key == right_key:
        return True
    if left == right:
        return True
    if left.isdigit() or right.isdigit():
        return False
    if min(len(left), len(right)) < 4:
        return False
    if len(left) <= 5 and len(right) <= 5 and left[:3] == right[:3]:
        return True
    if left.startswith(right) or right.startswith(left):
        return min(len(left), len(right)) / max(len(left), len(right)) >= 0.7
    return SequenceMatcher(None, left, right).ratio() >= 0.82


def canonical_token(token: str) -> str:
    for prefix, canonical in (
        ("emfan", "fain"),
        ("fain", "fain"),
        ("eix", "eix"),
        ("val", "val"),
        ("fer", "fer"),
        ("xreiaz", "xreiaz"),
        ("chreiaz", "xreiaz"),
    ):
        if token.startswith(prefix):
            return canonical
    return token


def longest_common_token_run(expected_tokens: list[str], candidate_tokens: list[str]) -> int:
    best = 0
    for expected_index in range(len(expected_tokens)):
        for candidate_index in range(len(candidate_tokens)):
            run = 0
            while (
                expected_index + run < len(expected_tokens)
                and candidate_index + run < len(candidate_tokens)
                and tokens_close(expected_tokens[expected_index + run], candidate_tokens[candidate_index + run])
            ):
                run += 1
            best = max(best, run)
    return best


def weighted_token_coverage(expected_tokens: list[str], candidate_tokens: list[str]) -> float:
    total = sum(token_weight(token) for token in expected_tokens)
    if not total:
        return 0.0
    matched = sum(token_weight(token) for token in expected_tokens if token_in(token, candidate_tokens))
    return matched / total


def token_weight(token: str) -> int:
    if token.isdigit():
        return 2
    if len(token) >= 7:
        return 2
    return 1


def regex_matches(pattern: str, value: str | None) -> bool:
    if value is None:
        return False
    try:
        return re.search(pattern, value, flags=re.IGNORECASE) is not None
    except re.error:
        return False


def tool_selection_correct(expected_tools: list[str], called_tools: list[str]) -> bool:
    return set(expected_tools).issubset(set(called_tools))
