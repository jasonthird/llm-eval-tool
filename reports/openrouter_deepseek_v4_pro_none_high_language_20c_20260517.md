# LLM Eval Report: `run_20260516_215445_e3dc013e`

- Generated: `2026-06-27T07:59:08.885640+00:00`
- Raw traces: `results/openrouter_deepseek_v4_pro_none_high_language_20c_20260517.jsonl`
- Task results: `216`
- Overall accuracy: `97.7%`
- Errors: `0`
- Total task latency: `3636.605s`
- Average task latency: `16.836s`
- Prompt tokens: `90136`
- Completion tokens: `79002`
- Total tokens: `169138`
- Cached tokens: `8738`
- Reasoning tokens: `71484`
- Estimated cost: `$0.333287`

## Accuracy by Task Type

- `single_turn`: `97.7%`

## Accuracy by Model

- `openrouter-deepseek-v4-pro-high`: `98.1%`
- `openrouter-deepseek-v4-pro-none`: `97.2%`

## Accuracy by Prompt

- `exact_reply`: `97.7%`

## Average Latency by Model

- `openrouter-deepseek-v4-pro-none`: `16.402s`
- `openrouter-deepseek-v4-pro-high`: `17.270s`

## Tokens by Model

- `openrouter-deepseek-v4-pro-none`: `82914`
- `openrouter-deepseek-v4-pro-high`: `86224`

## Estimated Cost by Model

- `openrouter-deepseek-v4-pro-none`: `$0.163099`
- `openrouter-deepseek-v4-pro-high`: `$0.170188`

## Tool Metrics

- Tool calls: `0`
- Tool selection accuracy: `0.0%`
- Invalid tool call rate: `0.0%`
- Python tool errors: `0`

## Tool Calls by Name

- No data.

## Python Errors by Model

- No data.

## Incorrect Answers

| Task | Type | Model | Expected | Extracted | Error |
|---|---|---|---|---|---|
| `language_understanding_178` | `single_turn` | `openrouter-deepseek-v4-pro-none` | `μόλις 17 εκατ. λιρών` | `17 εκατομμύρια λίρες` | `` |
| `language_understanding_168` | `single_turn` | `openrouter-deepseek-v4-pro-high` | `και μου ελεγες κατι για να μανατζαρω τις ωρες μου?` | `μανατζαρω τις ωρες μου` | `` |
| `language_understanding_169` | `single_turn` | `openrouter-deepseek-v4-pro-none` | `στα τέλη του 19ου αιώνα στο Ζίχοβο ("σήμ." Ζίβοβο) Μοριχόβου της Μακεδονίας` | `Ζίχοβο` | `` |
| `language_understanding_263` | `single_turn` | `openrouter-deepseek-v4-pro-none` | `πέντε φορές` | `5` | `` |
| `language_understanding_263` | `single_turn` | `openrouter-deepseek-v4-pro-high` | `πέντε φορές` | `5` | `` |

## Tool Failures

| Task | Model | Expected Tools | Called Tools | Invalid Calls | Error |
|---|---|---|---|---|---|
| - | - | - | - | - | - |
