import pytest

from llm_eval.runner import run_evaluation


@pytest.mark.asyncio
async def test_mock_mode_generates_results(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from pathlib import Path
    import shutil

    root = Path(__file__).resolve().parents[1]
    shutil.copytree(root / "configs", tmp_path / "configs")
    shutil.copytree(root / "data", tmp_path / "data")

    output = tmp_path / "results" / "mock.jsonl"
    finished = []
    async for event in run_evaluation(output_path=output, task_type="single_turn", mock_mode=True, run_id="run_mock"):
        if event.type == "TaskFinished":
            finished.append(event.payload["result"])
    assert output.exists()
    assert finished
    assert all(item.mock_mode for item in finished)
    sample_results = [item for item in finished if item.benchmark_name == "sample_math"]
    assert sample_results
    assert all(item.correct for item in sample_results)


@pytest.mark.asyncio
async def test_mock_tool_mode_uses_python(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from pathlib import Path
    import shutil

    root = Path(__file__).resolve().parents[1]
    shutil.copytree(root / "configs", tmp_path / "configs")
    shutil.copytree(root / "data", tmp_path / "data")

    output = tmp_path / "results" / "mock_tools.jsonl"
    finished = []
    async for event in run_evaluation(output_path=output, task_type="tool_calling", mock_mode=True, run_id="run_tools"):
        if event.type == "TaskFinished":
            finished.append(event.payload["result"])
    assert finished
    assert all(item.called_tools == ["python_exec"] for item in finished)
    assert all(item.tool_selection_correct for item in finished)
