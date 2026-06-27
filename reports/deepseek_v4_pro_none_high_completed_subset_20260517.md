# LLM Eval Report: `run_20260516_153111_9afdc14e`

- Generated: `2026-06-27T07:59:08.892203+00:00`
- Raw traces: `results/deepseek_v4_pro_none_high_completed_subset_20260517.jsonl`
- Task results: `81`
- Overall accuracy: `48.1%`
- Errors: `0`
- Total task latency: `181563.365s`
- Average task latency: `2241.523s`
- Prompt tokens: `318579`
- Completion tokens: `1024695`
- Total tokens: `1343274`
- Cached tokens: `284288`
- Reasoning tokens: `924117`
- Estimated cost: `$0.000000`

## Accuracy by Task Type

- `multi_turn`: `25.0%`
- `single_turn`: `64.6%`
- `tool_calling`: `23.1%`

## Accuracy by Model

- `deepseek-v4-pro-high`: `47.5%`
- `deepseek-v4-pro-none`: `48.8%`

## Accuracy by Prompt

- `default`: `48.1%`

## Average Latency by Model

- `deepseek-v4-pro-none`: `429.919s`
- `deepseek-v4-pro-high`: `4098.417s`

## Tokens by Model

- `deepseek-v4-pro-none`: `223906`
- `deepseek-v4-pro-high`: `1119368`

## Estimated Cost by Model

- `deepseek-v4-pro-none`: `$0.000000`
- `deepseek-v4-pro-high`: `$0.000000`

## Tool Metrics

- Tool calls: `62`
- Tool selection accuracy: `100.0%`
- Invalid tool call rate: `0.0%`
- Python tool errors: `11`

## Tool Calls by Name

- `python_exec`: `62`

## Python Errors by Model

- `deepseek-v4-pro-high`: `4`
- `deepseek-v4-pro-none`: `7`

## Incorrect Answers

| Task | Type | Model | Expected | Extracted | Error |
|---|---|---|---|---|---|
| `aimo3_ref_002` | `single_turn` | `deepseek-v4-pro-none` | `520` | `706` | `` |
| `aimo3_ref_006` | `single_turn` | `deepseek-v4-pro-none` | `32951` | `2` | `` |
| `aimo3_ref_007` | `single_turn` | `deepseek-v4-pro-none` | `57447` | `10` | `` |
| `aimo3_ref_004` | `single_turn` | `deepseek-v4-pro-none` | `580` | `291` | `` |
| `aimo3_ref_003` | `single_turn` | `deepseek-v4-pro-none` | `336` | `2002` | `` |
| `aimo3_ref_009` | `single_turn` | `deepseek-v4-pro-none` | `160` | `62` | `` |
| `aimo3_ref_005` | `single_turn` | `deepseek-v4-pro-none` | `21818` | `24288` | `` |
| `aimo3_mt_002` | `multi_turn` | `deepseek-v4-pro-none` | `520` | `706` | `` |
| `aimo3_ref_010` | `single_turn` | `deepseek-v4-pro-none` | `8687` | `1` | `` |
| `aimo3_mt_004` | `multi_turn` | `deepseek-v4-pro-none` | `580` | `292` | `` |
| `aimo3_mt_005` | `multi_turn` | `deepseek-v4-pro-none` | `21818` | `24194` | `` |
| `aimo3_ref_010` | `single_turn` | `deepseek-v4-pro-high` | `8687` | `` | `` |
| `aimo3_ref_007` | `single_turn` | `deepseek-v4-pro-high` | `57447` | `` | `` |
| `aimo3_ref_009` | `single_turn` | `deepseek-v4-pro-high` | `160` | `1` | `` |
| `aimo3_mt_007` | `multi_turn` | `deepseek-v4-pro-none` | `57447` | `15` | `` |
| `aimo3_mt_009` | `multi_turn` | `deepseek-v4-pro-none` | `160` | `8` | `` |
| `aimo3_mt_008` | `multi_turn` | `deepseek-v4-pro-none` | `32193` | `20` | `` |
| `aimo3_mt_010` | `multi_turn` | `deepseek-v4-pro-none` | `8687` | `49379` | `` |
| `aimo3_tool_001` | `tool_calling` | `deepseek-v4-pro-none` | `50` | `search` | `` |
| `aimo3_tool_001` | `tool_calling` | `deepseek-v4-pro-high` | `50` | `` | `` |
| `aimo3_tool_002` | `tool_calling` | `deepseek-v4-pro-high` | `520` | `` | `` |
| `aimo3_mt_005` | `multi_turn` | `deepseek-v4-pro-high` | `21818` | `` | `` |
| `aimo3_tool_003` | `tool_calling` | `deepseek-v4-pro-none` | `336` | `` | `` |
| `aimo3_tool_004` | `tool_calling` | `deepseek-v4-pro-none` | `580` | `` | `` |
| `aimo3_tool_003` | `tool_calling` | `deepseek-v4-pro-high` | `336` | `` | `` |
| `aimo3_tool_005` | `tool_calling` | `deepseek-v4-pro-none` | `21818` | `-1` | `` |
| `aimo3_mt_007` | `multi_turn` | `deepseek-v4-pro-high` | `57447` | `` | `` |
| `aimo3_tool_006` | `tool_calling` | `deepseek-v4-pro-high` | `32951` | `` | `` |
| `aimo3_tool_007` | `tool_calling` | `deepseek-v4-pro-none` | `57447` | `1` | `` |
| `aimo3_mt_009` | `multi_turn` | `deepseek-v4-pro-high` | `160` | `` | `` |
| `aimo3_tool_005` | `tool_calling` | `deepseek-v4-pro-high` | `21818` | `` | `` |
| `aimo3_mt_010` | `multi_turn` | `deepseek-v4-pro-high` | `8687` | `` | `` |
| `aimo3_ref_002` | `single_turn` | `deepseek-v4-pro-high` | `520` | `` | `` |
| `aimo3_ref_003` | `single_turn` | `deepseek-v4-pro-high` | `336` | `` | `` |
| `aimo3_ref_004` | `single_turn` | `deepseek-v4-pro-high` | `580` | `` | `` |
| `aimo3_ref_005` | `single_turn` | `deepseek-v4-pro-high` | `21818` | `` | `` |
| `aimo3_ref_006` | `single_turn` | `deepseek-v4-pro-high` | `32951` | `` | `` |
| `aimo3_ref_008` | `single_turn` | `deepseek-v4-pro-high` | `32193` | `` | `` |
| `aimo3_mt_002` | `multi_turn` | `deepseek-v4-pro-high` | `520` | `` | `` |
| `aimo3_mt_003` | `multi_turn` | `deepseek-v4-pro-none` | `336` | `` | `` |
| `aimo3_mt_003` | `multi_turn` | `deepseek-v4-pro-high` | `336` | `` | `` |
| `aimo3_mt_004` | `multi_turn` | `deepseek-v4-pro-high` | `580` | `` | `` |

## Tool Failures

| Task | Model | Expected Tools | Called Tools | Invalid Calls | Error |
|---|---|---|---|---|---|
| `aimo3_tool_001` | `deepseek-v4-pro-high` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
| `aimo3_tool_003` | `deepseek-v4-pro-none` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
| `aimo3_tool_004` | `deepseek-v4-pro-none` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
| `aimo3_tool_003` | `deepseek-v4-pro-high` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
| `aimo3_tool_007` | `deepseek-v4-pro-none` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
