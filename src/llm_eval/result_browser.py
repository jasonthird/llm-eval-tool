from __future__ import annotations

from pathlib import Path

from llm_eval.reporting import load_results


def list_result_files(results_dir: str | Path = "results") -> list[Path]:
    root = Path(results_dir)
    if not root.exists():
        return []
    return sorted(root.glob("*.jsonl"), key=lambda path: path.stat().st_mtime, reverse=True)


def incorrect_answers_text(path: str | Path) -> str:
    rows = [item for item in load_results(path) if not item.correct]
    if not rows:
        return "No incorrect answers."
    return "\n".join(
        f"{item.task_id} | {item.model_name} | expected={item.expected_answer} extracted={item.extracted_answer} error={item.error or '-'}"
        for item in rows
    )


def tool_failures_text(path: str | Path) -> str:
    rows = [
        item
        for item in load_results(path)
        if item.task_type == "tool_calling" and (item.invalid_tool_calls or item.tool_selection_correct is False)
    ]
    if not rows:
        return "No tool-calling failures."
    return "\n".join(
        f"{item.task_id} | {item.model_name} | expected={item.expected_tools} called={item.called_tools} invalid={len(item.invalid_tool_calls)}"
        for item in rows
    )
