# LLM Eval Report: `run_20260516_233503_f47ab5af`

- Generated: `2026-06-27T07:59:08.903270+00:00`
- Raw traces: `results/openrouter_gemma_4_31b_it_nitro_language_20c_20260517.jsonl`
- Task results: `108`
- Overall accuracy: `94.4%`
- Errors: `1`
- Total task latency: `283.062s`
- Average task latency: `2.621s`
- Prompt tokens: `43961`
- Completion tokens: `2983`
- Total tokens: `46944`
- Cached tokens: `8160`
- Reasoning tokens: `0`
- Estimated cost: `$0.006255`

## Accuracy by Task Type

- `single_turn`: `94.4%`

## Accuracy by Model

- `openrouter-gemma-4-31b-it-nitro`: `94.4%`

## Accuracy by Prompt

- `exact_reply`: `94.4%`

## Average Latency by Model

- `openrouter-gemma-4-31b-it-nitro`: `2.621s`

## Tokens by Model

- `openrouter-gemma-4-31b-it-nitro`: `46944`

## Estimated Cost by Model

- `openrouter-gemma-4-31b-it-nitro`: `$0.006255`

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
| `language_understanding_027` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `ποο μαλάκα πρώτη φορά μετά από δυο βδομάδες που χαλάρωσα` | `δυο βδομάδες που χαλάρωσα` | `` |
| `language_understanding_014` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `προς το παρόν κοιτάς το board Client Documentation` | `Client Documentation` | `` |
| `language_understanding_168` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `και μου ελεγες κατι για να μανατζαρω τις ωρες μου?` | `μανατζαρω τις ωρες μου` | `` |
| `language_understanding_215` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `ψήνει κανείς αύριο λάιβ αφιέρωμα στους Iron Maiden στο we?` | `Iron Maiden στο we` | `` |
| `language_understanding_228` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `ξεχνας εχω ios και πιθανοτατα να μην το εχει αυτο` | `μην το εχει αυτο` | `` |
| `language_understanding_077` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `εχω φτιαξει και "δεχτει" προσφορα, παω να κλεισω ραντεβου με τεχνικο και δινει αυτο` | `` | `Model call failed after 1 attempts: litellm.Timeout: Timeout Error: OpenrouterException - The operation was aborted` |

## Tool Failures

| Task | Model | Expected Tools | Called Tools | Invalid Calls | Error |
|---|---|---|---|---|---|
| - | - | - | - | - | - |
