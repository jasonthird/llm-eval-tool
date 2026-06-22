from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import Optional

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from llm_eval.config import ConfigValidationError, load_config, validate_config
from llm_eval.reporting import generate_markdown_report
from llm_eval.result_browser import incorrect_answers_text, list_result_files, tool_failures_text
from llm_eval.runner import run_evaluation
from llm_eval.schemas import EvaluationResult, new_run_id
from llm_eval.stats import LiveStats

app = typer.Typer(help="Async LLM/agent evaluation harness.")
console = Console()


def _apply_override(label: str, apply: Callable[[], None]) -> None:
    try:
        apply()
    except ValidationError as exc:
        raise typer.BadParameter(f"Invalid {label}: {exc.errors()[0]['msg']}") from exc


@app.command()
def run(
    mock: bool = typer.Option(False, "--mock", help="Use deterministic local mock responses."),
    task_type: Optional[str] = typer.Option(None, "--task-type", help="single_turn, multi_turn, tool_calling, or all."),
    benchmark: list[str] = typer.Option(None, "--benchmark", "-b", help="Benchmark name to run. Repeatable."),
    model: list[str] = typer.Option(None, "--model", "-m", help="Model name to run. Repeatable."),
    include: list[str] = typer.Option(
        None,
        "--include",
        "-i",
        help="Task id or category to include. Repeatable; comma-separated values are accepted.",
    ),
    exclude: list[str] = typer.Option(
        None,
        "--exclude",
        "-x",
        help="Task id or category to exclude. Repeatable; comma-separated values are accepted.",
    ),
    max_attempts: Optional[int] = typer.Option(None, "--max-attempts", help="Override retry attempts."),
    request_timeout: Optional[float] = typer.Option(None, "--request-timeout", help="Override per-request timeout seconds."),
    task_timeout: Optional[float] = typer.Option(None, "--task-timeout", help="Override per-task timeout seconds."),
    global_limit: Optional[int] = typer.Option(None, "--global-limit", help="Override total concurrent task calls."),
    per_model_limit: Optional[int] = typer.Option(None, "--per-model-limit", help="Override concurrent task calls per model."),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens", help="Override max output tokens for selected models."),
    context_size: Optional[int] = typer.Option(
        None,
        "--context-size",
        help="Alias for --max-tokens; use 65536 for a 64k reasoning/output budget when the provider supports it.",
    ),
    config_root: Path = typer.Option(Path("."), "--config-root", help="Resolve config and benchmark paths from this root."),
    output: Optional[Path] = typer.Option(None, "--output", help="Output JSONL trace path."),
    report_path: Optional[Path] = typer.Option(None, "--report-path", help="Output Markdown report path."),
) -> None:
    """Run an evaluation."""
    asyncio.run(
        _run_cli(
            mock=mock,
            task_type=task_type,
            benchmarks=benchmark,
            models=model,
            include=include,
            exclude=exclude,
            max_attempts=max_attempts,
            request_timeout=request_timeout,
            task_timeout=task_timeout,
            global_limit=global_limit,
            per_model_limit=per_model_limit,
            max_tokens=max_tokens,
            context_size=context_size,
            config_root=config_root,
            output=output,
            report_path=report_path,
        )
    )


async def _run_cli(
    mock: bool,
    task_type: str | None,
    benchmarks: list[str] | None,
    models: list[str] | None,
    include: list[str] | None,
    exclude: list[str] | None,
    max_attempts: int | None,
    request_timeout: float | None,
    task_timeout: float | None,
    global_limit: int | None,
    per_model_limit: int | None,
    max_tokens: int | None,
    context_size: int | None,
    config_root: Path,
    output: Path | None,
    report_path: Path | None,
) -> None:
    run_id = new_run_id()
    output = output or Path("results") / f"{run_id}.jsonl"
    config = _configured_app(
        benchmarks=benchmarks,
        models=models,
        max_attempts=max_attempts,
        request_timeout=request_timeout,
        task_timeout=task_timeout,
        global_limit=global_limit,
        per_model_limit=per_model_limit,
        max_tokens=max_tokens,
        context_size=context_size,
        config_root=config_root,
    )
    include_filter = parse_filter_values(include)
    exclude_filter = parse_filter_values(exclude)
    stats = LiveStats()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        progress_task = progress.add_task("running evaluation", total=None)
        async for event in run_evaluation(
            output_path=output,
            task_type=task_type,
            include=include_filter,
            exclude=exclude_filter,
            mock_mode=mock,
            config=config,
            run_id=run_id,
        ):
            if event.type == "TaskFinished":
                result: EvaluationResult = event.payload["result"]
                stats.update(result)
                progress.update(
                    progress_task,
                    description=(
                        f"tasks={stats.total} accuracy={stats.accuracy:.1%} errors={stats.errors} "
                        f"tokens={stats.total_tokens} cached={stats.cached_tokens} cost=${stats.cost_usd:.4f}"
                    ),
                )
            elif event.type == "RunFinished":
                elapsed = float(event.payload.get("elapsed_seconds", 0.0))
                progress.update(progress_task, description=f"evaluation complete in {elapsed:.2f}s")
    report = generate_markdown_report(output, report_path)
    console.print(f"[bold]Run ID:[/bold] {run_id}")
    console.print(f"[bold]Results:[/bold] {output}")
    console.print(f"[bold]Report:[/bold] {report}")
    console.print(f"[bold]Tokens:[/bold] {stats.total_tokens} total, {stats.cached_tokens} cached")
    console.print(f"[bold]Estimated cost:[/bold] ${stats.cost_usd:.6f}")
    if mock:
        console.print("[yellow]Mock mode was enabled; results are not benchmark claims.[/yellow]")


def _configured_app(
    *,
    benchmarks: list[str] | None,
    models: list[str] | None,
    max_attempts: int | None,
    request_timeout: float | None,
    task_timeout: float | None,
    global_limit: int | None,
    per_model_limit: int | None,
    max_tokens: int | None,
    context_size: int | None,
    config_root: Path = Path("."),
):
    config = load_config(root=config_root)
    if max_tokens is not None and context_size is not None and max_tokens != context_size:
        raise typer.BadParameter("--max-tokens and --context-size set the same value; provide only one or use matching values")
    token_budget = context_size if context_size is not None else max_tokens
    if benchmarks:
        selected = set(benchmarks)
        config.benchmarks = [benchmark for benchmark in config.benchmarks if benchmark.name in selected]
        missing = selected - {benchmark.name for benchmark in config.benchmarks}
        if missing:
            raise typer.BadParameter(f"Unknown benchmark(s): {', '.join(sorted(missing))}")
    if models:
        selected = set(models)
        config.models = [model for model in config.models if model.name in selected]
        missing = selected - {model.name for model in config.models}
        if missing:
            raise typer.BadParameter(f"Unknown model(s): {', '.join(sorted(missing))}")
    if max_attempts is not None:
        _apply_override("--max-attempts", lambda: setattr(config.runner.retries, "max_attempts", max_attempts))
    if request_timeout is not None:
        _apply_override(
            "--request-timeout",
            lambda: setattr(config.runner.timeouts, "request_timeout_seconds", request_timeout),
        )
    if task_timeout is not None:
        _apply_override("--task-timeout", lambda: setattr(config.runner.timeouts, "task_timeout_seconds", task_timeout))
    if global_limit is not None:
        _apply_override("--global-limit", lambda: setattr(config.runner.concurrency, "global_limit", global_limit))
    if per_model_limit is not None:
        _apply_override("--per-model-limit", lambda: setattr(config.runner.concurrency, "per_model_limit", per_model_limit))
    if token_budget is not None:
        for model in config.models:
            _apply_override("--max-tokens/--context-size", lambda model=model: setattr(model, "max_tokens", token_budget))
    _validate_or_raise(config)
    return config


def _validate_or_raise(config) -> None:
    try:
        validate_config(config)
    except ConfigValidationError as exc:
        raise typer.BadParameter(str(exc)) from exc


def parse_filter_values(values: list[str] | None) -> set[str] | None:
    if not values:
        return None
    parsed = {item.strip() for value in values for item in value.split(",") if item.strip()}
    return parsed or None


@app.command()
def validate(
    config_root: Path = typer.Option(Path("."), "--config-root", help="Resolve config and benchmark paths from this root."),
) -> None:
    """Validate configuration, benchmark files, and tool availability without running evaluations."""
    config = load_config(root=config_root)
    _validate_or_raise(config)
    console.print(
        f"[green]Configuration valid:[/green] {len(config.benchmarks)} benchmark(s), "
        f"{len(config.models)} model(s), {len(config.tools_enabled)} tool(s)."
    )


@app.command()
def list_config(
    config_root: Path = typer.Option(Path("."), "--config-root", help="Resolve config and benchmark paths from this root."),
) -> None:
    """List configured benchmarks and models."""
    config = load_config(root=config_root)
    console.print("[bold]Benchmarks[/bold]")
    for benchmark in config.benchmarks:
        console.print(f"- {benchmark.name} ({benchmark.task_type}) {benchmark.path}")
    console.print("[bold]Models[/bold]")
    for model in config.models:
        console.print(f"- {model.name} provider={model.provider} model={model.model} max_tokens={model.max_tokens}")


@app.command()
def report(
    results: Path = typer.Option(..., "--results", help="JSONL result path."),
    output: Optional[Path] = typer.Option(None, "--output", help="Markdown report output path."),
) -> None:
    """Generate a Markdown report from a JSONL trace."""
    report_file = generate_markdown_report(results, output)
    console.print(f"Report written to {report_file}")


@app.command()
def browse(
    results: Optional[Path] = typer.Option(
        None, "--results", help="JSONL result path. Defaults to the most recent file in results/."
    ),
) -> None:
    """Show incorrect answers and tool failures for a run."""
    path = results
    if path is None:
        files = list_result_files()
        if not files:
            console.print("[yellow]No result files found in results/.[/yellow]")
            raise typer.Exit(1)
        path = files[0]
    console.print(f"[bold]Results:[/bold] {path}")
    console.print("[bold]Incorrect answers[/bold]")
    console.print(incorrect_answers_text(path))
    console.print("[bold]Tool failures[/bold]")
    console.print(tool_failures_text(path))


if __name__ == "__main__":  # pragma: no cover
    app()
