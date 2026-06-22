from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from llm_eval.schemas import EvaluationResult


def load_results(path: str | Path) -> list[EvaluationResult]:
    results: list[EvaluationResult] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                results.append(EvaluationResult.model_validate(json.loads(line)))
    return results


def summarize(results: list[EvaluationResult]) -> dict[str, Any]:
    total = len(results)
    correct = sum(1 for item in results if item.correct)

    by_task_type = _group_accuracy(results, "task_type")
    by_model = _group_accuracy(results, "model_name")
    by_prompt = _group_accuracy(results, "prompt_name")
    latency_by_model: dict[str, float] = {}
    grouped: dict[str, list[EvaluationResult]] = defaultdict(list)
    for item in results:
        grouped[item.model_name].append(item)
    for model, items in grouped.items():
        latency_by_model[model] = mean(item.latency_seconds for item in items)
    cost_by_model = {model: sum(item.cost_usd for item in items) for model, items in grouped.items()}
    tokens_by_model = {model: sum(item.total_tokens for item in items) for model, items in grouped.items()}
    tool_results = [item for item in results if item.task_type == "tool_calling"]
    invalid_calls = sum(len(item.invalid_tool_calls) for item in tool_results)
    tool_calls = sum(len(item.tool_trace) + len(item.invalid_tool_calls) for item in tool_results)
    python_tool_errors = sum(
        1
        for item in tool_results
        for trace in item.tool_trace
        if trace.name == "python_exec" and trace.error
    )
    tool_calls_by_name: dict[str, int] = defaultdict(int)
    python_errors_by_model: dict[str, int] = defaultdict(int)
    for item in tool_results:
        for trace in item.tool_trace:
            tool_calls_by_name[trace.name] += 1
            if trace.name == "python_exec" and trace.error:
                python_errors_by_model[item.model_name] += 1
        for invalid in item.invalid_tool_calls:
            tool_calls_by_name[str(invalid.get("name") or "invalid")] += 1
    selection_known = [item for item in tool_results if item.tool_selection_correct is not None]
    tool_selection_accuracy = (
        sum(1 for item in selection_known if item.tool_selection_correct) / len(selection_known)
        if selection_known
        else 0.0
    )
    return {
        "total": total,
        "correct": correct,
        "overall_accuracy": correct / total if total else 0.0,
        "by_task_type": by_task_type,
        "by_model": by_model,
        "by_prompt": by_prompt,
        "latency_by_model": latency_by_model,
        "total_task_latency_seconds": sum(item.latency_seconds for item in results),
        "average_task_latency_seconds": mean(item.latency_seconds for item in results) if results else 0.0,
        "prompt_tokens": sum(item.prompt_tokens for item in results),
        "completion_tokens": sum(item.completion_tokens for item in results),
        "total_tokens": sum(item.total_tokens for item in results),
        "cached_tokens": sum(item.cached_tokens for item in results),
        "reasoning_tokens": sum(item.reasoning_tokens for item in results),
        "cost_usd": sum(item.cost_usd for item in results),
        "cost_by_model": cost_by_model,
        "tokens_by_model": tokens_by_model,
        "tool_selection_accuracy": tool_selection_accuracy,
        "invalid_tool_call_rate": invalid_calls / tool_calls if tool_calls else 0.0,
        "tool_call_count": tool_calls,
        "tool_calls_by_name": dict(sorted(tool_calls_by_name.items())),
        "python_tool_errors": python_tool_errors,
        "python_errors_by_model": dict(sorted(python_errors_by_model.items())),
        "errors": sum(1 for item in results if item.error),
    }


def _group_accuracy(results: list[EvaluationResult], attr: str) -> dict[str, float]:
    grouped: dict[str, list[EvaluationResult]] = defaultdict(list)
    for item in results:
        grouped[str(getattr(item, attr))].append(item)
    return {
        key: sum(1 for item in items if item.correct) / len(items)
        for key, items in sorted(grouped.items())
        if items
    }


def generate_markdown_report(results_path: str | Path, output_path: str | Path | None = None) -> Path:
    results_path = Path(results_path)
    results = load_results(results_path)
    summary = summarize(results)
    run_id = results[0].run_id if results else results_path.stem
    output = Path(output_path) if output_path else Path("reports") / f"{run_id}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    incorrect = [item for item in results if not item.correct]
    tool_failures = [
        item
        for item in results
        if item.task_type == "tool_calling"
        and (
            item.error
            or item.invalid_tool_calls
            or item.tool_selection_correct is False
            or any(trace.error for trace in item.tool_trace)
        )
    ]

    lines = [
        f"# LLM Eval Report: `{run_id}`",
        "",
        f"- Generated: `{now}`",
        f"- Raw traces: `{results_path}`",
        f"- Task results: `{summary['total']}`",
        f"- Overall accuracy: `{summary['overall_accuracy']:.1%}`",
        f"- Errors: `{summary['errors']}`",
        f"- Total task latency: `{summary['total_task_latency_seconds']:.3f}s`",
        f"- Average task latency: `{summary['average_task_latency_seconds']:.3f}s`",
        f"- Prompt tokens: `{summary['prompt_tokens']}`",
        f"- Completion tokens: `{summary['completion_tokens']}`",
        f"- Total tokens: `{summary['total_tokens']}`",
        f"- Cached tokens: `{summary['cached_tokens']}`",
        f"- Reasoning tokens: `{summary['reasoning_tokens']}`",
        f"- Estimated cost: `${summary['cost_usd']:.6f}`",
        "",
        "## Accuracy by Task Type",
        "",
        *_metric_lines(summary["by_task_type"]),
        "",
        "## Accuracy by Model",
        "",
        *_metric_lines(summary["by_model"]),
        "",
        "## Accuracy by Prompt",
        "",
        *_metric_lines(summary["by_prompt"]),
        "",
        "## Average Latency by Model",
        "",
        *_metric_lines(summary["latency_by_model"], suffix="s", precision=3),
        "",
        "## Tokens by Model",
        "",
        *_metric_lines(summary["tokens_by_model"], suffix="", precision=0),
        "",
        "## Estimated Cost by Model",
        "",
        *_metric_lines(summary["cost_by_model"], suffix="$", precision=6),
        "",
        "## Tool Metrics",
        "",
        f"- Tool calls: `{summary['tool_call_count']}`",
        f"- Tool selection accuracy: `{summary['tool_selection_accuracy']:.1%}`",
        f"- Invalid tool call rate: `{summary['invalid_tool_call_rate']:.1%}`",
        f"- Python tool errors: `{summary['python_tool_errors']}`",
        "",
        "## Tool Calls by Name",
        "",
        *_metric_lines(summary["tool_calls_by_name"], suffix="", precision=0),
        "",
        "## Python Errors by Model",
        "",
        *_metric_lines(summary["python_errors_by_model"], suffix="", precision=0),
        "",
        "## Incorrect Answers",
        "",
        "| Task | Type | Model | Expected | Extracted | Error |",
        "|---|---|---|---|---|---|",
    ]
    lines.extend(
        f"| `{item.task_id}` | `{item.task_type}` | `{item.model_name}` | `{item.expected_answer}` | `{item.extracted_answer}` | `{item.error or ''}` |"
        for item in incorrect
    )
    if not incorrect:
        lines.append("| - | - | - | - | - | - |")
    lines.extend(
        [
            "",
            "## Tool Failures",
            "",
            "| Task | Model | Expected Tools | Called Tools | Invalid Calls | Error |",
            "|---|---|---|---|---|---|",
        ]
    )
    lines.extend(
        f"| `{item.task_id}` | `{item.model_name}` | `{', '.join(item.expected_tools)}` | `{', '.join(item.called_tools)}` | `{len(item.invalid_tool_calls)}` | `{item.error or ''}` |"
        for item in tool_failures
    )
    if not tool_failures:
        lines.append("| - | - | - | - | - | - |")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def _metric_lines(values: dict[str, float], suffix: str = "%", precision: int = 1) -> list[str]:
    if not values:
        return ["- No data."]
    if suffix == "%":
        return [f"- `{key}`: `{value:.1%}`" for key, value in values.items()]
    if suffix == "$":
        return [f"- `{key}`: `${value:.{precision}f}`" for key, value in values.items()]
    if suffix == "":
        return [f"- `{key}`: `{value:.{precision}f}`" for key, value in values.items()]
    return [f"- `{key}`: `{value:.{precision}f}{suffix}`" for key, value in values.items()]
