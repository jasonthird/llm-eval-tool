from __future__ import annotations

import re

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


def regex_matches(pattern: str, value: str | None) -> bool:
    if value is None:
        return False
    try:
        return re.search(pattern, value, flags=re.IGNORECASE) is not None
    except re.error:
        return False


def tool_selection_correct(expected_tools: list[str], called_tools: list[str]) -> bool:
    return set(expected_tools).issubset(set(called_tools))
