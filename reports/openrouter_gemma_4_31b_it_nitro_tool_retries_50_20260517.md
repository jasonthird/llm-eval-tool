# Agent Eval Report: `run_20260516_234412_cdc5fcb3`

- Generated: `2026-05-17T00:04:13.339338+00:00`
- Raw traces: `results/openrouter_gemma_4_31b_it_nitro_tool_retries_50_20260517.jsonl`
- Task results: `12`
- Overall accuracy: `25.0%`
- Errors: `0`
- Total task latency: `12244.595s`
- Average task latency: `1020.383s`
- Prompt tokens: `19653`
- Completion tokens: `8833`
- Total tokens: `28486`
- Cached tokens: `0`
- Reasoning tokens: `0`
- Estimated cost: `$0.008264`

## Accuracy by Task Type

- `tool_calling`: `25.0%`

## Accuracy by Model

- `openrouter-gemma-4-31b-it-nitro`: `25.0%`

## Accuracy by Prompt

- `default`: `25.0%`

## Average Latency by Model

- `openrouter-gemma-4-31b-it-nitro`: `1020.383s`

## Tokens by Model

- `openrouter-gemma-4-31b-it-nitro`: `28486`

## Estimated Cost by Model

- `openrouter-gemma-4-31b-it-nitro`: `$0.008264`

## Tool Metrics

- Tool calls: `9`
- Tool selection accuracy: `100.0%`
- Invalid tool call rate: `0.0%`
- Python tool errors: `1`

## Tool Calls by Name

- `python_exec`: `9`

## Python Errors by Model

- `openrouter-gemma-4-31b-it-nitro`: `1`

## Incorrect Answers

| Task | Type | Model | Expected | Extracted | Error |
|---|---|---|---|---|---|
| `aimo3_tool_001` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `50` | `` | `` |
| `aimo3_tool_002` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `520` | `` | `` |
| `aimo3_tool_003` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `336` | `` | `` |
| `aimo3_tool_004` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `580` | `` | `` |
| `aimo3_tool_005` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `21818` | `` | `` |
| `aimo3_tool_006` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `32951` | `` | `` |
| `aimo3_tool_007` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `57447` | `` | `` |
| `aimo3_tool_008` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `32193` | `` | `` |
| `aimo3_tool_010` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `8687` | `` | `` |

## Tool Failures

| Task | Model | Expected Tools | Called Tools | Invalid Calls | Error |
|---|---|---|---|---|---|
| `aimo3_tool_009` | `openrouter-gemma-4-31b-it-nitro` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
