from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

FINAL_RE = re.compile(r"FINAL_ANSWER\s*:\s*(.+)", re.IGNORECASE | re.DOTALL)
BOXED_RE = re.compile(r"\\boxed\{([^{}]+)\}")
NUMBER_RE = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?")


def extract_answer(text: str | None) -> str:
    if not text:
        return ""
    text = text.strip()
    final = FINAL_RE.search(text)
    if final:
        return clean_candidate(final.group(1))
    boxed = BOXED_RE.findall(text)
    if boxed:
        return clean_candidate(boxed[-1])
    numbers = NUMBER_RE.findall(text)
    if numbers:
        return clean_candidate(numbers[-1])
    tokens = [token for token in re.findall(r"[\w.-]+", text) if re.search(r"\w", token)]
    return clean_candidate(tokens[-1] if tokens else text)


def clean_candidate(value: str) -> str:
    value = value.strip()
    value = value.splitlines()[0].strip()
    value = re.sub(r"^[`*_'\" \t]+|[`*_'\" \t]+$", "", value)
    value = re.sub(r"[.!?;,:\s]+$", "", value)
    return value.strip()


def normalize_answer(value: str | None) -> str:
    if value is None:
        return ""
    value = str(value).strip().lower()
    value = value.replace(",", "")
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"^[`*_'\" ]+|[`*_'\" ]+$", "", value)
    value = re.sub(r"[.!?;,:\s]+$", "", value)
    return value.strip()


def as_decimal(value: str | None) -> Decimal | None:
    normalized = normalize_answer(value)
    if not normalized:
        return None
    try:
        return Decimal(normalized)
    except InvalidOperation:
        return None
