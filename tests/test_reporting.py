import json

from agent_eval.reporting import generate_markdown_report, load_results, summarize
from agent_eval.schemas import EvaluationResult, ToolTrace
from agent_eval.result_browser import incorrect_answers_text, list_result_files, tool_failures_text
from agent_eval.stats import LiveStats


def make_result(**overrides):
    data = {
        "run_id": "run_report",
        "task_id": "task",
        "task_type": "single_turn",
        "benchmark_name": "bench",
        "category": "cat",
        "model_name": "model",
        "model": "mock/model",
        "prompt_name": "default",
        "expected_answer": "42",
        "raw_response": "FINAL_ANSWER: 42",
        "extracted_answer": "42",
        "correct": True,
        "latency_seconds": 0.1,
    }
    data.update(overrides)
    return EvaluationResult(**data)


def write_results(path, results):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(result.model_dump_json() for result in results) + "\n", encoding="utf-8")


def test_reporting_summary_markdown_and_result_browser(tmp_path):
    results_path = tmp_path / "results" / "run.jsonl"
    report_path = tmp_path / "reports" / "run.md"
    results = [
        make_result(),
        make_result(
            task_id="bad",
            correct=False,
            extracted_answer="41",
            error="wrong",
            latency_seconds=0.3,
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            cached_tokens=3,
            reasoning_tokens=2,
            cost_usd=0.01,
        ),
        make_result(
            task_id="tool",
            task_type="tool_calling",
            expected_tools=["python_exec"],
            called_tools=["python_exec"],
            tool_trace=[ToolTrace(name="python_exec", args={"code": "print(42)"}, output="42")],
            tool_selection_correct=True,
            total_tokens=7,
            cost_usd=0.02,
        ),
        make_result(
            task_id="tool_bad",
            task_type="tool_calling",
            expected_tools=["python_exec"],
            called_tools=["python_exec"],
            tool_trace=[ToolTrace(name="python_exec", args={"code": "raise Exception()"}, error="failed")],
            invalid_tool_calls=[{"name": "python_exec", "arguments": "{", "error": "bad json"}],
            tool_selection_correct=False,
        ),
    ]
    write_results(results_path, results)

    loaded = load_results(results_path)
    summary = summarize(loaded)
    assert summary["total"] == 4
    assert summary["overall_accuracy"] == 0.75
    assert summary["invalid_tool_call_rate"] == 1 / 3
    assert summary["tool_selection_accuracy"] == 0.5
    assert summary["tool_call_count"] == 3
    assert summary["tool_calls_by_name"]["python_exec"] == 3
    assert summary["python_tool_errors"] == 1
    assert summary["python_errors_by_model"]["model"] == 1
    assert summary["total_task_latency_seconds"] == 0.6
    assert summary["prompt_tokens"] == 10
    assert summary["completion_tokens"] == 5
    assert summary["total_tokens"] == 22
    assert summary["cached_tokens"] == 3
    assert summary["reasoning_tokens"] == 2
    assert summary["cost_usd"] == 0.03
    assert summary["tokens_by_model"]["model"] == 22
    assert summary["cost_by_model"]["model"] == 0.03

    generated = generate_markdown_report(results_path, report_path)
    text = generated.read_text(encoding="utf-8")
    assert "tool_bad" in text
    assert "Overall accuracy" in text
    assert "Estimated cost" in text
    assert "Cached tokens" in text
    assert "Tool calls" in text
    assert "Python tool errors" in text
    assert "Invalid Calls | Error" in text

    assert list_result_files(tmp_path / "missing") == []
    assert list_result_files(tmp_path / "results") == [results_path]
    assert "bad | model" in incorrect_answers_text(results_path)
    assert "tool_bad | model" in tool_failures_text(results_path)


def test_reporting_empty_and_clean_browser_messages(tmp_path):
    empty_path = tmp_path / "empty.jsonl"
    empty_path.write_text("", encoding="utf-8")
    report = generate_markdown_report(empty_path)
    assert report.exists()
    assert summarize([])["overall_accuracy"] == 0.0

    clean_path = tmp_path / "clean.jsonl"
    write_results(clean_path, [make_result()])
    assert incorrect_answers_text(clean_path) == "No incorrect answers."
    assert tool_failures_text(clean_path) == "No tool-calling failures."


def test_live_stats_defaults_and_average():
    stats = LiveStats()
    assert stats.accuracy == 0.0
    assert stats.average_latency == 0.0
    stats.total = 2
    stats.correct = 1
    stats.latency_sum = 3
    assert stats.accuracy == 0.5
    assert stats.average_latency == 1.5
