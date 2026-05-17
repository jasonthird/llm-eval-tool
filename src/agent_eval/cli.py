from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from agent_eval.config import load_config
from agent_eval.reporting import generate_markdown_report
from agent_eval.runner import run_evaluation
from agent_eval.schemas import EvaluationResult, new_run_id

app = typer.Typer(help="Async LLM/agent evaluation harness.")
console = Console()


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
    )
    include_filter = parse_filter_values(include)
    exclude_filter = parse_filter_values(exclude)
    seen = correct = errors = tokens = cached_tokens = 0
    cost = 0.0
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
                seen += 1
                correct += int(result.correct)
                errors += int(result.error is not None)
                tokens += result.total_tokens
                cached_tokens += result.cached_tokens
                cost += result.cost_usd
                progress.update(
                    progress_task,
                    description=(
                        f"tasks={seen} accuracy={correct / seen:.1%} errors={errors} "
                        f"tokens={tokens} cached={cached_tokens} cost=${cost:.4f}"
                    ),
                )
            elif event.type == "RunFinished":
                elapsed = float(event.payload.get("elapsed_seconds", 0.0))
                progress.update(progress_task, description=f"evaluation complete in {elapsed:.2f}s")
    report = generate_markdown_report(output, report_path)
    console.print(f"[bold]Run ID:[/bold] {run_id}")
    console.print(f"[bold]Results:[/bold] {output}")
    console.print(f"[bold]Report:[/bold] {report}")
    console.print(f"[bold]Tokens:[/bold] {tokens} total, {cached_tokens} cached")
    console.print(f"[bold]Estimated cost:[/bold] ${cost:.6f}")
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
):
    config = load_config()
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
        config.runner.retries.max_attempts = max_attempts
    if request_timeout is not None:
        config.runner.timeouts.request_timeout_seconds = request_timeout
    if task_timeout is not None:
        config.runner.timeouts.task_timeout_seconds = task_timeout
    if global_limit is not None:
        config.runner.concurrency.global_limit = global_limit
    if per_model_limit is not None:
        config.runner.concurrency.per_model_limit = per_model_limit
    if token_budget is not None:
        for model in config.models:
            model.max_tokens = token_budget
    return config


def parse_filter_values(values: list[str] | None) -> set[str] | None:
    if not values:
        return None
    parsed = {item.strip() for value in values for item in value.split(",") if item.strip()}
    return parsed or None


@app.command()
def list_config() -> None:
    """List configured benchmarks and models."""
    config = load_config()
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


if __name__ == "__main__":  # pragma: no cover
    app()
