import json

from agent_eval.schemas import EvaluationResult


def test_trace_schema_round_trip():
    result = EvaluationResult(
        run_id="run_test",
        task_id="math_001",
        task_type="single_turn",
        benchmark_name="sample_math",
        category="arithmetic",
        model_name="mock",
        model="mock/model",
        prompt_name="default",
        expected_answer="391",
        raw_response="FINAL_ANSWER: 391",
        extracted_answer="391",
        correct=True,
        latency_seconds=0.01,
        prompt_tokens=7,
        completion_tokens=3,
        total_tokens=10,
        cached_tokens=2,
        reasoning_tokens=1,
        cost_usd=0.004,
        mock_mode=True,
    )
    encoded = result.model_dump_json()
    decoded = EvaluationResult.model_validate(json.loads(encoded))
    assert decoded.correct is True
    assert decoded.mock_mode is True
    assert decoded.total_tokens == 10
    assert decoded.cached_tokens == 2
    assert decoded.cost_usd == 0.004
