# LLM Eval Report: `run_20260516_233644_bf85bb79`

- Generated: `2026-06-27T07:59:08.881883+00:00`
- Raw traces: `results/openrouter_gemma_4_31b_it_nitro_all_active_combined_20260517.jsonl`
- Task results: `156`
- Overall accuracy: `83.3%`
- Errors: `1`
- Total task latency: `15354.772s`
- Average task latency: `98.428s`
- Prompt tokens: `84910`
- Completion tokens: `79478`
- Total tokens: `164388`
- Cached tokens: `10112`
- Reasoning tokens: `0`
- Estimated cost: `$0.042588`

## Accuracy by Task Type

- `multi_turn`: `58.3%`
- `single_turn`: `90.9%`
- `tool_calling`: `25.0%`

## Accuracy by Model

- `openrouter-gemma-4-31b-it-nitro`: `83.3%`

## Accuracy by Prompt

- `default`: `58.3%`
- `exact_reply`: `94.4%`

## Average Latency by Model

- `openrouter-gemma-4-31b-it-nitro`: `98.428s`

## Tokens by Model

- `openrouter-gemma-4-31b-it-nitro`: `164388`

## Estimated Cost by Model

- `openrouter-gemma-4-31b-it-nitro`: `$0.042588`

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
| `aimo3_ref_003` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `336` | `120` | `` |
| `aimo3_ref_004` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `580` | `442` | `` |
| `aimo3_ref_005` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `21818` | `62138` | `` |
| `aimo3_ref_007` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `57447` | `1` | `` |
| `aimo3_ref_009` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `160` | `156` | `` |
| `aimo3_ref_010` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `8687` | `21` | `` |
| `aimo3_mt_002` | `multi_turn` | `openrouter-gemma-4-31b-it-nitro` | `520` | `707` | `` |
| `aimo3_mt_005` | `multi_turn` | `openrouter-gemma-4-31b-it-nitro` | `21818` | `22141` | `` |
| `aimo3_mt_007` | `multi_turn` | `openrouter-gemma-4-31b-it-nitro` | `57447` | `<answer>10</answer>` | `` |
| `aimo3_mt_009` | `multi_turn` | `openrouter-gemma-4-31b-it-nitro` | `160` | `<answer>158</answer>` | `` |
| `aimo3_mt_010` | `multi_turn` | `openrouter-gemma-4-31b-it-nitro` | `8687` | `21` | `` |
| `aimo3_tool_001` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `50` | `` | `` |
| `aimo3_tool_002` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `520` | `` | `` |
| `aimo3_tool_003` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `336` | `` | `` |
| `aimo3_tool_004` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `580` | `` | `` |
| `aimo3_tool_005` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `21818` | `` | `` |
| `aimo3_tool_006` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `32951` | `` | `` |
| `aimo3_tool_007` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `57447` | `` | `` |
| `aimo3_tool_008` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `32193` | `` | `` |
| `aimo3_tool_010` | `tool_calling` | `openrouter-gemma-4-31b-it-nitro` | `8687` | `` | `` |
| `language_understanding_014` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `προς το παρόν κοιτάς το board Client Documentation` | `Client Documentation` | `` |
| `language_understanding_027` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `ποο μαλάκα πρώτη φορά μετά από δυο βδομάδες που χαλάρωσα` | `δυο βδομάδες που χαλάρωσα` | `` |
| `language_understanding_077` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `εχω φτιαξει και "δεχτει" προσφορα, παω να κλεισω ραντεβου με τεχνικο και δινει αυτο` | `` | `Model call failed after 1 attempts: litellm.Timeout: Timeout Error: OpenrouterException - The operation was aborted` |
| `language_understanding_168` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `και μου ελεγες κατι για να μανατζαρω τις ωρες μου?` | `μανατζαρω τις ωρες μου` | `` |
| `language_understanding_215` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `ψήνει κανείς αύριο λάιβ αφιέρωμα στους Iron Maiden στο we?` | `Iron Maiden στο we` | `` |
| `language_understanding_228` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `ξεχνας εχω ios και πιθανοτατα να μην το εχει αυτο` | `μην το εχει αυτο` | `` |

## Tool Failures

| Task | Model | Expected Tools | Called Tools | Invalid Calls | Error |
|---|---|---|---|---|---|
| `aimo3_tool_009` | `openrouter-gemma-4-31b-it-nitro` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
