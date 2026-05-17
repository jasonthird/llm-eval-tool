# Evaluation Results

This page summarizes the curated comparison artifacts for DeepSeek Flash, DeepSeek Pro, and Gemma 4.

## Current Model Set

| Model family | Config entries used in reports |
|---|---|
| DeepSeek V4 Flash | `deepseek-v4-flash-none`, `deepseek-v4-flash-high` |
| DeepSeek V4 Pro | `openrouter-deepseek-v4-pro-none`, `openrouter-deepseek-v4-pro-high`, completed OpenCode Pro subset |
| Gemma 4 | `openrouter-gemma-4-31b-it-nitro` |

## Curated Result Artifacts

```text
results/deepseek_v4_flash_thinking_none_high_all_active_20260516.jsonl
reports/deepseek_v4_flash_thinking_none_high_all_active_20260516.md

results/openrouter_deepseek_v4_pro_none_high_language_20c_20260517.jsonl
reports/openrouter_deepseek_v4_pro_none_high_language_20c_20260517.md

results/deepseek_v4_pro_none_high_all_active_4h_15c_20260516.jsonl
reports/deepseek_v4_pro_none_high_all_active_4h_15c_20260516.md

results/deepseek_v4_pro_none_high_completed_subset_20260517.jsonl
reports/deepseek_v4_pro_none_high_completed_subset_20260517.md

results/openrouter_gemma_4_31b_it_nitro_all_active_combined_20260517.jsonl
reports/openrouter_gemma_4_31b_it_nitro_all_active_combined_20260517.md

results/openrouter_gemma_4_31b_it_nitro_language_20c_20260517.jsonl
reports/openrouter_gemma_4_31b_it_nitro_language_20c_20260517.md

results/openrouter_gemma_4_31b_it_nitro_remaining_active_20c_retry_20260517.jsonl

results/openrouter_gemma_4_31b_it_nitro_tool_retries_50_20260517.jsonl
reports/openrouter_gemma_4_31b_it_nitro_tool_retries_50_20260517.md
```

## Published Charts

```text
docs/images/model-language-accuracy.svg
docs/images/model-language-latency.svg
docs/images/model-aimo-accuracy.svg
```

## Local Test Suite

- Command: `UV_CACHE_DIR=.uv-cache uv run pytest -q`
- Result: `46 passed`
- Coverage: `100.00%`

## Dataset Notes

- `language_understanding` is Greek-focused and includes Greek, Greeklish, mixed Greek/Latin, and imperfect/non-standard Greek.
- `sample_math` has 8 arithmetic tasks.
- `sample_logic` has 6 ordering, parity, and deductive logic tasks.
- AIMO3 reference tasks are intentionally hard and are reported separately from language-understanding conclusions.
