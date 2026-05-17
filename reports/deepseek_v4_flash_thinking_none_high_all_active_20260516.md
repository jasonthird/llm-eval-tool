# Agent Eval Report: `run_20260516_123947_ef05407e`

- Generated: `2026-05-16T14:55:37.071666+00:00`
- Raw traces: `results/deepseek_v4_flash_thinking_none_high_all_active_20260516.jsonl`
- Task results: `312`
- Overall accuracy: `82.7%`
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

- `multi_turn`: `50.0%`
- `single_turn`: `91.3%`
- `tool_calling`: `20.8%`

## Accuracy by Model

- `deepseek-v4-flash-high`: `84.6%`
- `deepseek-v4-flash-none`: `80.8%`

## Accuracy by Prompt

- `default`: `56.2%`
- `exact_reply`: `94.4%`

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
| `language_understanding_075` | `single_turn` | `deepseek-v4-flash-none` | `den einai data/disaster recovery einai ena bare minimum na exoume backups k na kseroume pws na ginei twra` | `bare minimum na exoume backups k na kseroume pws na ginei twra` | `` |
| `language_understanding_066` | `single_turn` | `deepseek-v4-flash-high` | `για αρχη θα τα ανεβασω ετσι και απο δευτερα που θα εχω τελειωσει σιγουρα με αυτα που επειγουν για το launch θα το τσεκαρω` | `τσεκαρω` | `` |
| `language_understanding_111` | `single_turn` | `deepseek-v4-flash-none` | `7 Φεβρουαρίου 1906` | `1906` | `` |
| `language_understanding_124` | `single_turn` | `deepseek-v4-flash-none` | `Kali timi kani h alithia einai, den ksero an einai kalos omos` | `den ksero an einai kalos omos` | `` |
| `language_understanding_168` | `single_turn` | `deepseek-v4-flash-none` | `και μου ελεγες κατι για να μανατζαρω τις ωρες μου?` | `να μανατζαρω τις ωρες μου` | `` |
| `language_understanding_174` | `single_turn` | `deepseek-v4-flash-high` | `Τη Δευτερα θα σας πω επισης πως θα κανουμε απο εδω και περα τα tasks, δλδ πως θα φτανει ενα task να ειναι branch που γινεται merge request` | `πως θα κανουμε απο εδω και περα τα tasks, δλδ πως θα φτανει ενα task να ειναι branch που γινεται merge request` | `` |
| `language_understanding_198` | `single_turn` | `deepseek-v4-flash-none` | `πιο συγκεκριμενα, αυτη τη στιγμη βαζει consumables και chemicals και device modes. Θελουμε ή να τα φτιαχνουν μονοι τους αυτα?` | `αυτη τη στιγμη βαζει consumables και chemicals και device modes` | `` |
| `language_understanding_194` | `single_turn` | `deepseek-v4-flash-high` | `Μαλλον το εριξα για λιγο με ολα τα runners να τρεχουν ασταματητα` | `ασταματητα` | `` |
| `language_understanding_214` | `single_turn` | `deepseek-v4-flash-none` | `καθομαι και εγω σα μαλακας και κανω κανονικα τη διαδικασια` | `κανω κανονικα τη διαδικασια` | `` |
| `language_understanding_231` | `single_turn` | `deepseek-v4-flash-none` | `, apla /summary kai tha sou bgali to command na to patisis, einai ligo periergo to pos doulebi sto discord auto` | `auto` | `` |
| `language_understanding_255` | `single_turn` | `deepseek-v4-flash-none` | `Christina Applegate` | `Applegate` | `` |
| `language_understanding_262` | `single_turn` | `deepseek-v4-flash-high` | `Ο 2ος παντα θα εχει του πρωτου να δει σα μπουσουλα οποτε δε θα τρωει και τοσο χρονο` | `2` | `` |
| `aimo3_ref_002` | `single_turn` | `deepseek-v4-flash-none` | `520` | `999` | `` |
| `aimo3_ref_005` | `single_turn` | `deepseek-v4-flash-none` | `21818` | `62140` | `` |
| `aimo3_ref_004` | `single_turn` | `deepseek-v4-flash-none` | `580` | `1000` | `` |
| `aimo3_ref_006` | `single_turn` | `deepseek-v4-flash-none` | `32951` | `1` | `` |
| `aimo3_ref_007` | `single_turn` | `deepseek-v4-flash-none` | `57447` | `1` | `` |
| `aimo3_ref_009` | `single_turn` | `deepseek-v4-flash-none` | `160` | `70` | `` |
| `aimo3_ref_010` | `single_turn` | `deepseek-v4-flash-none` | `8687` | `11` | `` |
| `aimo3_mt_002` | `multi_turn` | `deepseek-v4-flash-none` | `520` | `520.The maximum number of rectangles with distinct perimeters that can tile a 500×500 square is 520, achieved by using rectangles of dimensions 1×1, 1×2, …, 1×500 (500 rectangles) and 500×2, 500×3, …, 500×21 (20 rectangles), with adjustments to area to exactly fill the square. The remainder when 520 is divided by \(10^5\) is 520` | `` |
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
| `aimo3_tool_008` | `tool_calling` | `deepseek-v4-flash-none` | `32193` | `10` | `` |
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
| `aimo3_tool_009` | `tool_calling` | `deepseek-v4-flash-none` | `160` | `8` | `` |
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
