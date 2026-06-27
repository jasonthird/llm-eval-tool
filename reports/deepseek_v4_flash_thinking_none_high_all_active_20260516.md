# LLM Eval Report: `run_20260516_123947_ef05407e`

- Generated: `2026-06-27T07:59:08.917352+00:00`
- Raw traces: `results/deepseek_v4_flash_thinking_none_high_all_active_20260516.jsonl`
- Task results: `312`
- Overall accuracy: `87.2%`
- Errors: `0`
- Total task latency: `20327.430s`
- Average task latency: `65.152s`
- Prompt tokens: `728542`
- Completion tokens: `1194718`
- Total tokens: `1923260`
- Cached tokens: `573824`
- Reasoning tokens: `823681`
- Estimated cost: `$0.000000`

## Accuracy by Task Type

- `multi_turn`: `54.2%`
- `single_turn`: `95.5%`
- `tool_calling`: `29.2%`

## Accuracy by Model

- `deepseek-v4-flash-high`: `87.2%`
- `deepseek-v4-flash-none`: `87.2%`

## Accuracy by Prompt

- `default`: `59.4%`
- `exact_reply`: `99.5%`

## Average Latency by Model

- `deepseek-v4-flash-high`: `109.524s`
- `deepseek-v4-flash-none`: `20.780s`

## Tokens by Model

- `deepseek-v4-flash-high`: `1262225`
- `deepseek-v4-flash-none`: `661035`

## Estimated Cost by Model

- `deepseek-v4-flash-high`: `$0.000000`
- `deepseek-v4-flash-none`: `$0.000000`

## Tool Metrics

- Tool calls: `97`
- Tool selection accuracy: `95.8%`
- Invalid tool call rate: `0.0%`
- Python tool errors: `19`

## Tool Calls by Name

- `calculator_add`: `1`
- `python_exec`: `96`

## Python Errors by Model

- `deepseek-v4-flash-high`: `14`
- `deepseek-v4-flash-none`: `5`

## Incorrect Answers

| Task | Type | Model | Expected | Extracted | Error |
|---|---|---|---|---|---|
| `language_understanding_168` | `single_turn` | `deepseek-v4-flash-none` | `και μου ελεγες κατι για να μανατζαρω τις ωρες μου?` | `να μανατζαρω τις ωρες μου` | `` |
| `aimo3_ref_002` | `single_turn` | `deepseek-v4-flash-none` | `520` | `999` | `` |
| `aimo3_ref_005` | `single_turn` | `deepseek-v4-flash-none` | `21818` | `62140` | `` |
| `aimo3_ref_004` | `single_turn` | `deepseek-v4-flash-none` | `580` | `1000` | `` |
| `aimo3_ref_006` | `single_turn` | `deepseek-v4-flash-none` | `32951` | `1` | `` |
| `aimo3_ref_007` | `single_turn` | `deepseek-v4-flash-none` | `57447` | `1` | `` |
| `aimo3_ref_009` | `single_turn` | `deepseek-v4-flash-none` | `160` | `70` | `` |
| `aimo3_ref_010` | `single_turn` | `deepseek-v4-flash-none` | `8687` | `11` | `` |
| `aimo3_ref_002` | `single_turn` | `deepseek-v4-flash-high` | `520` | `` | `` |
| `aimo3_mt_006` | `multi_turn` | `deepseek-v4-flash-none` | `32951` | `1` | `` |
| `aimo3_mt_005` | `multi_turn` | `deepseek-v4-flash-none` | `21818` | `62140` | `` |
| `aimo3_mt_007` | `multi_turn` | `deepseek-v4-flash-none` | `57447` | `1` | `` |
| `aimo3_ref_007` | `single_turn` | `deepseek-v4-flash-high` | `57447` | `` | `` |
| `aimo3_ref_009` | `single_turn` | `deepseek-v4-flash-high` | `160` | `` | `` |
| `aimo3_ref_010` | `single_turn` | `deepseek-v4-flash-high` | `8687` | `` | `` |
| `aimo3_mt_009` | `multi_turn` | `deepseek-v4-flash-none` | `160` | `5` | `` |
| `aimo3_mt_010` | `multi_turn` | `deepseek-v4-flash-none` | `8687` | `17901` | `` |
| `aimo3_tool_002` | `tool_calling` | `deepseek-v4-flash-none` | `520` | `` | `` |
| `aimo3_mt_002` | `multi_turn` | `deepseek-v4-flash-high` | `520` | `` | `` |
| `aimo3_mt_003` | `multi_turn` | `deepseek-v4-flash-high` | `336` | `` | `` |
| `aimo3_tool_003` | `tool_calling` | `deepseek-v4-flash-none` | `336` | `this` | `` |
| `aimo3_tool_004` | `tool_calling` | `deepseek-v4-flash-none` | `580` | `` | `` |
| `aimo3_tool_005` | `tool_calling` | `deepseek-v4-flash-none` | `21818` | `` | `` |
| `aimo3_tool_001` | `tool_calling` | `deepseek-v4-flash-high` | `50` | `` | `` |
| `aimo3_tool_006` | `tool_calling` | `deepseek-v4-flash-none` | `32951` | `1024` | `` |
| `aimo3_tool_007` | `tool_calling` | `deepseek-v4-flash-none` | `57447` | `1` | `` |
| `aimo3_mt_005` | `multi_turn` | `deepseek-v4-flash-high` | `21818` | `` | `` |
| `aimo3_tool_002` | `tool_calling` | `deepseek-v4-flash-high` | `520` | `` | `` |
| `aimo3_tool_003` | `tool_calling` | `deepseek-v4-flash-high` | `336` | `` | `` |
| `aimo3_tool_004` | `tool_calling` | `deepseek-v4-flash-high` | `580` | `` | `` |
| `aimo3_tool_010` | `tool_calling` | `deepseek-v4-flash-none` | `8687` | `` | `` |
| `aimo3_tool_006` | `tool_calling` | `deepseek-v4-flash-high` | `32951` | `` | `` |
| `aimo3_tool_005` | `tool_calling` | `deepseek-v4-flash-high` | `21818` | `` | `` |
| `aimo3_tool_008` | `tool_calling` | `deepseek-v4-flash-high` | `32193` | `` | `` |
| `aimo3_tool_007` | `tool_calling` | `deepseek-v4-flash-high` | `57447` | `` | `` |
| `aimo3_tool_010` | `tool_calling` | `deepseek-v4-flash-high` | `8687` | `` | `` |
| `aimo3_mt_007` | `multi_turn` | `deepseek-v4-flash-high` | `57447` | `` | `` |
| `aimo3_tool_009` | `tool_calling` | `deepseek-v4-flash-high` | `160` | `` | `` |
| `aimo3_mt_009` | `multi_turn` | `deepseek-v4-flash-high` | `160` | `` | `` |
| `aimo3_mt_010` | `multi_turn` | `deepseek-v4-flash-high` | `8687` | `` | `` |

## Tool Failures

| Task | Model | Expected Tools | Called Tools | Invalid Calls | Error |
|---|---|---|---|---|---|
| `aimo3_tool_001` | `deepseek-v4-flash-none` | `python_exec` | `python_exec, python_exec, python_exec` | `0` | `` |
| `aimo3_tool_003` | `deepseek-v4-flash-none` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
| `aimo3_tool_004` | `deepseek-v4-flash-none` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
| `aimo3_tool_005` | `deepseek-v4-flash-none` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
| `aimo3_tool_001` | `deepseek-v4-flash-high` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
| `aimo3_tool_002` | `deepseek-v4-flash-high` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
| `aimo3_tool_003` | `deepseek-v4-flash-high` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
| `aimo3_tool_004` | `deepseek-v4-flash-high` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
| `aimo3_tool_010` | `deepseek-v4-flash-none` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
| `aimo3_tool_005` | `deepseek-v4-flash-high` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
| `aimo3_tool_008` | `deepseek-v4-flash-high` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
| `aimo3_tool_007` | `deepseek-v4-flash-high` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
| `aimo3_tool_010` | `deepseek-v4-flash-high` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
| `aimo3_tool_009` | `deepseek-v4-flash-none` | `python_exec` | `` | `0` | `` |
| `aimo3_tool_009` | `deepseek-v4-flash-high` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
