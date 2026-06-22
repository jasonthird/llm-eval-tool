from pathlib import Path

import pytest

from llm_eval.config import ConfigValidationError, load_config, load_tasks, load_yaml, validate_config


def write_valid_config(root: Path, *, benchmark_path: str = "data/tasks.jsonl", tools: list[str] | None = None) -> None:
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
    enabled_tools = tools or ["python_exec"]
    (root / "configs" / "tools.yaml").write_text(
        "tools:\n  enabled:\n" + "".join(f"    - {tool}\n" for tool in enabled_tools),
        encoding="utf-8",
    )
    (root / "configs" / "runner.yaml").write_text("runner: {}\n", encoding="utf-8")
    (root / benchmark_path).write_text(
        '{"id":"task","task_type":"single_turn","question":"Q?","answer":"A"}\n',
        encoding="utf-8",
    )


def test_load_yaml_empty_file(tmp_path):
    path = tmp_path / "empty.yaml"
    path.write_text("", encoding="utf-8")
    assert load_yaml(path) == {}


def test_load_config_and_invalid_task(tmp_path):
    models = tmp_path / "models.yaml"
    prompts = tmp_path / "prompts.yaml"
    benchmarks = tmp_path / "benchmarks.yaml"
    tools = tmp_path / "tools.yaml"
    runner = tmp_path / "runner.yaml"
    data = tmp_path / "tasks.jsonl"

    models.write_text(
        "providers:\n  - name: mock\n    api_key_env: MOCK_KEY\nmodels:\n  - name: mock\n    provider: mock\n    model: mock/model\n",
        encoding="utf-8",
    )
    prompts.write_text("prompts:\n  - name: default\n    system: system\n", encoding="utf-8")
    benchmarks.write_text(f"benchmarks:\n  - name: sample\n    task_type: single_turn\n    path: {data}\n", encoding="utf-8")
    tools.write_text("tools:\n  enabled:\n    - python_exec\n", encoding="utf-8")
    runner.write_text("runner: {}\n", encoding="utf-8")
    data.write_text("\nnot json\n", encoding="utf-8")

    config = load_config(models, prompts, benchmarks, tools, runner)
    assert config.models[0].name == "mock"
    assert config.provider_by_name("mock").api_key_env == "MOCK_KEY"
    assert config.provider_by_name("implicit").name == "implicit"
    assert config.tools_enabled == ["python_exec"]

    with pytest.raises(ValueError, match="Invalid task JSONL"):
        load_tasks(Path(data))


def test_load_config_resolves_benchmark_paths_from_explicit_root(tmp_path):
    write_valid_config(tmp_path)

    config = load_config(root=tmp_path)

    assert Path(config.benchmarks[0].path) == tmp_path / "data" / "tasks.jsonl"
    validate_config(config)


def test_validate_config_rejects_cross_reference_failures(tmp_path):
    write_valid_config(tmp_path)
    config = load_config(root=tmp_path)
    config.models[0].provider = "missing-provider"
    config.benchmarks[0].prompt = "missing-prompt"
    config.benchmarks[0].path = str(tmp_path / "data" / "missing.jsonl")
    config.tools_enabled = ["missing-tool"]

    with pytest.raises(ConfigValidationError) as exc_info:
        validate_config(config)

    message = str(exc_info.value)
    assert "unknown provider 'missing-provider'" in message
    assert "unknown prompt 'missing-prompt'" in message
    assert "file does not exist" in message
    assert "Configured tool 'missing-tool' is not available" in message


def test_validate_config_rejects_duplicate_names(tmp_path):
    write_valid_config(tmp_path)
    config = load_config(root=tmp_path)
    config.models.append(config.models[0].model_copy())
    config.prompts.append(config.prompts[0].model_copy())
    config.benchmarks.append(config.benchmarks[0].model_copy())
    config.tools_enabled.append(config.tools_enabled[0])

    with pytest.raises(ConfigValidationError) as exc_info:
        validate_config(config)

    message = str(exc_info.value)
    assert "Duplicate model name 'mock'" in message
    assert "Duplicate prompt name 'default'" in message
    assert "Duplicate benchmark name 'sample'" in message
    assert "Duplicate enabled tool name 'python_exec'" in message


def test_validate_config_rejects_malformed_benchmark_data(tmp_path):
    write_valid_config(tmp_path)
    (tmp_path / "data" / "tasks.jsonl").write_text("not json\n", encoding="utf-8")
    config = load_config(root=tmp_path)

    with pytest.raises(ConfigValidationError, match="Invalid task JSONL"):
        validate_config(config)


def test_validate_config_rejects_task_type_and_expected_tool_mismatch(tmp_path):
    write_valid_config(tmp_path, tools=["calculator_add"])
    (tmp_path / "data" / "tasks.jsonl").write_text(
        '{"id":"task","task_type":"tool_calling","question":"Q?","answer":"A","expected_tools":["python_exec"]}\n',
        encoding="utf-8",
    )
    config = load_config(root=tmp_path)

    with pytest.raises(ConfigValidationError) as exc_info:
        validate_config(config)

    message = str(exc_info.value)
    assert "expected 'single_turn'" in message
    assert "expects disabled tool 'python_exec'" in message


def test_aimo3_reference_tasks_load():
    math_tasks = load_tasks("data/sample_math.jsonl")
    logic_tasks = load_tasks("data/sample_logic.jsonl")
    assert len(math_tasks) == 8
    assert math_tasks[-1].answer == "243"
    assert len(logic_tasks) == 6
    assert logic_tasks[-1].answer_regex == r"\bblue\b"

    tasks = load_tasks("data/aimo3_reference.jsonl")
    assert len(tasks) == 10
    assert tasks[0].id == "aimo3_ref_001"
    assert tasks[-1].answer == "8687"


def test_aimo3_multiturn_and_python_tool_tasks_load():
    config = load_config()
    benchmarks = {benchmark.name: benchmark for benchmark in config.benchmarks}
    assert benchmarks["aimo3_reference_multiturn"].task_type == "multi_turn"
    assert benchmarks["aimo3_reference_python_tools"].task_type == "tool_calling"

    multiturn = load_tasks("data/aimo3_reference_multiturn.jsonl")
    tool_tasks = load_tasks("data/aimo3_reference_tools.jsonl")
    assert len(multiturn) == 10
    assert len(tool_tasks) == 10
    assert multiturn[0].id == "aimo3_mt_001"
    assert multiturn[0].turns[-1].content == "Now complete the solution. End with exactly FINAL_ANSWER: <answer>."
    assert tool_tasks[0].id == "aimo3_tool_001"
    assert tool_tasks[0].expected_tools == ["python_exec"]
    assert tool_tasks[-1].answer == "8687"


def test_language_understanding_tasks_load():
    config = load_config()
    benchmarks = {benchmark.name: benchmark for benchmark in config.benchmarks}
    assert benchmarks["language_understanding"].prompt == "exact_reply"

    tasks = load_tasks("data/language_understanding.jsonl")
    categories = {task.category for task in tasks}
    assert len(tasks) == 108
    assert tasks[0].id == "language_understanding_001"
    assert tasks[0].category == "greek"
    assert tasks[0].answer == "ή μιλούσες μόνος σου και δεν κατάλαβες ότι είσαι μόνος;"
    assert tasks[1].answer_regex == r"Σφαίρα\w*[\s\S]*Screen\w*[\s\S]*Actors\w*"
    assert categories == {"broken_greeklish", "english_or_other_latin", "greek", "mixed_greek_latin"}
