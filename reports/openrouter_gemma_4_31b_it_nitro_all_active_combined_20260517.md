# Agent Eval Report: `run_20260516_233644_bf85bb79`

- Generated: `2026-05-17T03:56:45.174777+00:00`
- Raw traces: `results/openrouter_gemma_4_31b_it_nitro_all_active_combined_20260517.jsonl`
- Task results: `156`
- Overall accuracy: `76.3%`
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

- `multi_turn`: `50.0%`
- `single_turn`: `83.3%`
- `tool_calling`: `25.0%`

## Accuracy by Model

- `openrouter-gemma-4-31b-it-nitro`: `76.3%`

## Accuracy by Prompt

- `default`: `56.2%`
- `exact_reply`: `85.2%`

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
| `aimo3_mt_008` | `multi_turn` | `openrouter-gemma-4-31b-it-nitro` | `32193` | `<answer>32193</answer>` | `` |
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
| `language_understanding_036` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `και μετα ολοι θα πρεπει να φερετε το local σας στη κατασταση που θα ειναι το remote` | `φερετε το local σας στη κατασταση που θα ειναι το remote` | `` |
| `language_understanding_058` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `μικρη λεπτομερια αλλα το κουμπι στην δημιουργια χημικων γραφει απλα δημιουργια` | `δημιουργια χημικων γραφει απλα δημιουργια` | `` |
| `language_understanding_073` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `Να σε βγάζει βίντεο από την κάμερα όταν βλέπεις βίντεο για ενήλικες` | `κάμερα όταν βλέπεις βίντεο για ενήλικες` | `` |
| `language_understanding_077` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `εχω φτιαξει και "δεχτει" προσφορα, παω να κλεισω ραντεβου με τεχνικο και δινει αυτο` | `` | `Model call failed after 1 attempts: litellm.Timeout: Timeout Error: OpenrouterException - The operation was aborted` |
| `language_understanding_146` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `επισης πρεπει να τους βαλω στην αλλη λιστα αλλιως δεν αρκει` | `αλλη λιστα αλλιως δεν αρκει` | `` |
| `language_understanding_148` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `χελλοου πιπολ, δεν ξερω εαν ειναι bug αλλα δεν με αφηνει να κανω καταγραφη δραστηριοτητας σε ενα lead μου ( και απο τον γενικο πινακα αλλα και απο την καρτελα τα leads μου )` | `δεν με αφηνει να κανω καταγραφη δραστηριοτητας σε ενα lead μου ( και απο τον γενικο πινακα αλλα και απο την καρτελα τα leads μου )` | `` |
| `language_understanding_168` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `και μου ελεγες κατι για να μανατζαρω τις ωρες μου?` | `μανατζαρω τις ωρες μου` | `` |
| `language_understanding_174` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `Τη Δευτερα θα σας πω επισης πως θα κανουμε απο εδω και περα τα tasks, δλδ πως θα φτανει ενα task να ειναι branch που γινεται merge request` | `πως θα κανουμε απο εδω και περα τα tasks, δλδ πως θα φτανει ενα task να ειναι branch που γινεται merge request` | `` |
| `language_understanding_177` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `άρα κάνατε πως θα σηκώνατε την βάση; τα επόμενα βήματα είναι να σηκώνετε app services for frontend backend and chirpstack?` | `βάση; τα επόμενα βήματα είναι να σηκώνετε app services for frontend backend and chirpstack` | `` |
| `language_understanding_196` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `αρχοντή όταν τελειώσεις με το build θες να με βοηθήσεις με κάποιες παρουσιάσεις που πρέπει να γίνουν; να στήσουμε λίγο το customer acquisition γιατί ο γιώργος δεν ξέρει τα processess for SaaS businesses` | `θες να με βοηθήσεις με κάποιες παρουσιάσεις που πρέπει να γίνουν; να στήσουμε λίγο το customer acquisition γιατί ο γιώργος δεν ξέρει τα processess for SaaS businesses` | `` |
| `language_understanding_214` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `καθομαι και εγω σα μαλακας και κανω κανονικα τη διαδικασια` | `κανω κανονικα τη διαδικασια` | `` |
| `language_understanding_215` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `ψήνει κανείς αύριο λάιβ αφιέρωμα στους Iron Maiden στο we?` | `Iron Maiden στο we` | `` |
| `language_understanding_221` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `to vraveio Emmy, to Screen Actors Guild Award` | `Emmy, to Screen Actors Guild Award` | `` |
| `language_understanding_228` | `single_turn` | `openrouter-gemma-4-31b-it-nitro` | `ξεχνας εχω ios και πιθανοτατα να μην το εχει αυτο` | `μην το εχει αυτο` | `` |

## Tool Failures

| Task | Model | Expected Tools | Called Tools | Invalid Calls | Error |
|---|---|---|---|---|---|
| `aimo3_tool_009` | `openrouter-gemma-4-31b-it-nitro` | `python_exec` | `python_exec, python_exec, python_exec, python_exec, python_exec, python_exec, python_exec` | `0` | `` |
