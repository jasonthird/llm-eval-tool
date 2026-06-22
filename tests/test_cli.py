from pathlib import Path

import pytest
from typer.testing import CliRunner

from llm_eval import cli
from llm_eval.cli import _configured_app, _run_cli, app, parse_filter_values
from llm_eval.events import run_finished, task_finished
from llm_eval.schemas import EvaluationResult


def write_valid_config(root: Path, *, benchmark_path: str = "data/tasks.jsonl") -> None:
    (root / "configs").mkdir()
    (root / "data").mkdir()
    (root / "configs" / "models.yaml").write_text(
        "providers:\n  - name: mock\n    api_key_env: MOCK_KEY\n"
        "models:\n  - name: mock\n    provider: mock\n    model: mock/model\n",
        encoding="utf-8",
    )
    (root / "configs" / "prompts.yaml").write_text(
        "prompts:\n  - name: default\n    system: system\n",
        encoding="utf-8",
    )
    (root / "configs" / "benchmarks.yaml").write_text(
        f"benchmarks:\n  - name: sample\n    task_type: single_turn\n    path: {benchmark_path}\n    prompt: default\n",
        encoding="utf-8",
    )
    (root / "configs" / "tools.yaml").write_text("tools:\n  enabled:\n    - python_exec\n", encoding="utf-8")
    (root / "configs" / "runner.yaml").write_text("runner: {}\n", encoding="utf-8")
    (root / benchmark_path).write_text(
        '{"id":"task","task_type":"single_turn","question":"Q?","answer":"A"}\n',
        encoding="utf-8",
    )


def result() -> EvaluationResult:
    return EvaluationResult(
        run_id="run_cli",
        task_id="task",
        task_type="single_turn",
        benchmark_name="bench",
        category="cat",
        model_name="model",
        model="mock/model",
        prompt_name="default",
        expected_answer="42",
        raw_response="FINAL_ANSWER: 42",
        extracted_answer="42",
        correct=True,
        latency_seconds=0.1,
        total_tokens=12,
        cached_tokens=4,
        cost_usd=0.25,
        mock_mode=True,
    )


@pytest.mark.asyncio
async def test_run_cli_prints_paths(monkeypatch, tmp_path):
    async def fake_run_evaluation(**kwargs):
        yield task_finished(kwargs["run_id"], result())
        yield run_finished(
            kwargs["run_id"],
            total=1,
            failures=0,
            output_path=str(kwargs["output_path"]),
            elapsed_seconds=1.25,
        )

    def fake_report(output, report_path):
        assert output == tmp_path / "results.jsonl"
        return report_path

    monkeypatch.setattr(cli, "run_evaluation", fake_run_evaluation)
    monkeypatch.setattr(cli, "generate_markdown_report", fake_report)
    await _run_cli(
        True,
        "single_turn",
        [],
        [],
        ["greek"],
        ["language_understanding_003"],
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        Path("."),
        tmp_path / "results.jsonl",
        tmp_path / "report.md",
    )


def test_cli_commands(monkeypatch, tmp_path):
    runner = CliRunner()
    calls = {}

    def fake_asyncio_run(coro):
        calls["coro"] = coro
        coro.close()

    def fake_report(results: Path, output: Path | None):
        calls["report"] = (results, output)
        return output or Path("report.md")

    monkeypatch.setattr(cli.asyncio, "run", fake_asyncio_run)
    monkeypatch.setattr(cli, "generate_markdown_report", fake_report)

    run_result = runner.invoke(
        app,
        [
            "run",
            "--mock",
            "--benchmark",
            "sample_math",
            "--model",
            "deepseek-v4-flash-none",
            "--include",
            "greek,broken_greeklish",
            "--exclude",
            "language_understanding_003",
            "--max-attempts",
            "1",
            "--request-timeout",
            "2",
            "--task-timeout",
            "3",
            "--global-limit",
            "10",
            "--per-model-limit",
            "5",
            "--max-tokens",
            "4",
            "--context-size",
            "4",
            "--config-root",
            ".",
            "--output",
            str(tmp_path / "out.jsonl"),
        ],
    )
    assert run_result.exit_code == 0
    assert "coro" in calls

    list_result = runner.invoke(app, ["list-config"])
    assert list_result.exit_code == 0
    assert "Benchmarks" in list_result.output

    validate_result = runner.invoke(app, ["validate"])
    assert validate_result.exit_code == 0
    assert "Configuration valid" in validate_result.output

    report_result = runner.invoke(app, ["report", "--results", str(tmp_path / "out.jsonl")])
    assert report_result.exit_code == 0
    assert calls["report"][0] == tmp_path / "out.jsonl"


def test_browse_command(tmp_path):
    runner = CliRunner()
    results_path = tmp_path / "out.jsonl"
    rows = [
        result(),
        result().model_copy(update={"task_id": "bad", "correct": False, "extracted_answer": "41"}),
    ]
    results_path.write_text("\n".join(row.model_dump_json() for row in rows) + "\n", encoding="utf-8")

    found = runner.invoke(app, ["browse", "--results", str(results_path)])
    assert found.exit_code == 0
    assert "bad" in found.output

    missing = runner.invoke(app, ["browse", "--results", str(tmp_path / "missing")])
    assert missing.exit_code != 0


def test_browse_defaults_to_latest_result(monkeypatch, tmp_path):
    runner = CliRunner()
    results_path = tmp_path / "out.jsonl"
    results_path.write_text(result().model_dump_json() + "\n", encoding="utf-8")

    monkeypatch.setattr(cli, "list_result_files", lambda: [results_path])
    latest = runner.invoke(app, ["browse"])
    assert latest.exit_code == 0
    assert "Incorrect answers" in latest.output

    monkeypatch.setattr(cli, "list_result_files", lambda: [])
    empty = runner.invoke(app, ["browse"])
    assert empty.exit_code == 1
    assert "No result files found" in empty.output


def test_configured_app_filters_and_overrides():
    config = _configured_app(
        benchmarks=["sample_math"],
        models=["deepseek-v4-flash-none"],
        max_attempts=1,
        request_timeout=2,
        task_timeout=3,
        global_limit=10,
        per_model_limit=5,
        max_tokens=4,
        context_size=None,
    )
    assert [benchmark.name for benchmark in config.benchmarks] == ["sample_math"]
    assert [model.name for model in config.models] == ["deepseek-v4-flash-none"]
    assert config.runner.retries.max_attempts == 1
    assert config.runner.timeouts.request_timeout_seconds == 2
    assert config.runner.timeouts.task_timeout_seconds == 3
    assert config.runner.concurrency.global_limit == 10
    assert config.runner.concurrency.per_model_limit == 5
    assert config.models[0].max_tokens == 4

    context_config = _configured_app(
        benchmarks=["sample_math"],
        models=["deepseek-v4-flash-none"],
        max_attempts=None,
        request_timeout=None,
        task_timeout=None,
        global_limit=None,
        per_model_limit=None,
        max_tokens=None,
        context_size=65536,
    )
    assert context_config.models[0].max_tokens == 65536


def test_parse_filter_values():
    assert parse_filter_values(None) is None
    assert parse_filter_values([]) is None
    assert parse_filter_values(["greek, broken_greeklish", "language_understanding_003"]) == {
        "greek",
        "broken_greeklish",
        "language_understanding_003",
    }


def test_configured_app_rejects_unknown_names():
    with pytest.raises(Exception, match="Unknown benchmark"):
        _configured_app(
            benchmarks=["missing"],
            models=None,
            max_attempts=None,
            request_timeout=None,
            task_timeout=None,
            global_limit=None,
            per_model_limit=None,
            max_tokens=None,
            context_size=None,
        )
    with pytest.raises(Exception, match="Unknown model"):
        _configured_app(
            benchmarks=None,
            models=["missing"],
            max_attempts=None,
            request_timeout=None,
            task_timeout=None,
            global_limit=None,
            per_model_limit=None,
            max_tokens=None,
            context_size=None,
        )
    with pytest.raises(Exception, match="same value"):
        _configured_app(
            benchmarks=None,
            models=None,
            max_attempts=None,
            request_timeout=None,
            task_timeout=None,
            global_limit=None,
            per_model_limit=None,
            max_tokens=2048,
            context_size=65536,
        )


@pytest.mark.parametrize(
    ("override", "value"),
    [
        ("max_attempts", 0),
        ("request_timeout", 0),
        ("task_timeout", 0),
        ("global_limit", 0),
        ("per_model_limit", 0),
        ("max_tokens", 0),
    ],
)
def test_configured_app_rejects_invalid_positive_overrides(override, value):
    kwargs = {
        "benchmarks": None,
        "models": None,
        "max_attempts": None,
        "request_timeout": None,
        "task_timeout": None,
        "global_limit": None,
        "per_model_limit": None,
        "max_tokens": None,
        "context_size": None,
    }
    kwargs[override] = value
    with pytest.raises(Exception, match="Invalid"):
        _configured_app(**kwargs)


def test_validate_command_uses_config_root_and_reports_errors(tmp_path):
    write_valid_config(tmp_path)
    runner = CliRunner()

    valid = runner.invoke(app, ["validate", "--config-root", str(tmp_path)])
    assert valid.exit_code == 0
    assert "Configuration valid" in valid.output

    (tmp_path / "configs" / "benchmarks.yaml").write_text(
        "benchmarks:\n  - name: sample\n    task_type: single_turn\n    path: data/missing.jsonl\n    prompt: default\n",
        encoding="utf-8",
    )
    invalid = runner.invoke(app, ["validate", "--config-root", str(tmp_path)])
    assert invalid.exit_code != 0
    assert "file does not exist" in invalid.output
