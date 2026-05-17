from agent_eval.extraction import as_decimal, extract_answer, normalize_answer


def test_extract_prefers_final_answer():
    assert extract_answer("Reasoning...\nFINAL_ANSWER: 1,234.") == "1,234"
    assert extract_answer("FINAL_ANSWER: **50**") == "50"
    assert extract_answer(None) == ""


def test_extract_boxed_then_number():
    assert extract_answer("Therefore \\boxed{42}") == "42"
    assert extract_answer("The result is about 18.") == "18"
    assert extract_answer("Answer is cobalt.") == "cobalt"
    assert extract_answer("Το κείμενο αναφέρεται στη Μάχη των Θερμοπυλών.") == "Θερμοπυλών"
    assert extract_answer("!!!") == ""


def test_normalize_answer():
    assert normalize_answer(" 1,234. ") == "1234"
    assert normalize_answer("**50**") == "50"
    assert normalize_answer("Hello   World!") == "hello world"
    assert normalize_answer(None) == ""


def test_as_decimal_empty_and_invalid():
    assert as_decimal("") is None
    assert as_decimal("not-a-number") is None
