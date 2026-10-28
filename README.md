# context-rot-lab

This is a small test harness. It checks which **context failure modes** still break today's coding agents. It puts each failure into a real agent's context window, applies the usual fix, and grades the result with hidden tests the agent never sees.

It accompanies the Prompt Engineering video "Context Rot Is Mostly Solved. Except This One."

## The task

The agent has one job: migrate a small `orders` service from an old database driver (`legacydb`) to a new one (`newdb`). The catch is that `newdb.connect()` makes **one** connection attempt and never retries on its own, so the existing retry loops in `orders/db.py` and `orders/reports.py` must stay.

The visible tests (`repo_template/tests/`) check behavior and that `legacydb` is gone. The hidden tests (`hidden_tests/test_hidden.py`) add two retry checks, so an agent can pass every visible test and still ship the bug. `reference/` holds a correct migration, and it passes all 12 tests.

## The 13 setups

| Setup | What is injected into the context | Fix applied |
|---|---|---|
| `clean` | Nothing | — |
| `poison` | A wrong self-note ("newdb retries automatically, delete the retry loops") from a truncated docs read | — |
| `poison_validate` | Same note | A validator call checks the note against the docs first |
| `clash` | The wrong note, about 25K tokens of history, then a correction | — |
| `clash_prune` | Only the correction | The wrong note is deleted |
| `distract60` / `distract160` | About 60K or 145K tokens of the agent's own past log reads | — |
| `distract160_compact` | About 145K tokens of history | The model summarizes it into a handoff note |
| `tools30` / `tools100` | 30 or 95 tool definitions, including traps such as `write_file_legacy` | — |
| `tools100_search` | 95 tools in a catalog | Only the 6 core tools plus `search_tools` |
| `selfcond_silent` | The agent's own earlier migration of `db.py` silently dropped the retry loop | — |
| `selfcond_feedback` | Same, plus a canary log that shows requests failing during a failover | Evidence from the environment |

`tools100` is named for the 100 tools requested. The tool catalog holds only 95 (6 core, 4 traps, 85 generic).

## Results (5 runs per cell, low reasoning effort)

| Setup | Qwen3.8 Flash-Next | Qwen3.8 27B | Gemini 3.8 Flash |
|---|---|---|---|
| clean | 5/5 | 5/5 | 5/5 |
| poison | 5/5 | 5/5 | 5/5 |
| clash | 5/5 | 5/5 | 5/5 |
| distraction, ~60K tokens | 5/5 | 4/5 | 5/5 |
| distraction, ~145K tokens | 5/5 | 5/5 | 5/5 |
| 95 tools | 5/5 | 5/5 | 5/5 |
| **own bug, silent** | **0/5** | **0/5** | **0/5** |
| own bug + canary log | 4/5 | 2/5 | 4/5 |

Compaction kept every pass and cut the prompt tokens per run by 23x to 59x. The full table, with every cell, is in `results_final.txt`. Each run's trace, token counts and final files are in `results/<lane>/<cell>/<seed>.json`.

This is one task with 5 runs per cell, so treat the numbers as a demonstration, not a benchmark.

## Run it

You need Python 3.11+ and pytest. The Qwen lanes need OpenAI-compatible servers (vLLM in the video), and the Gemini lane needs an API key.

```bash
export GEMINI_API_KEY=...                                   # gemini lane
export FLASH_URL=http://localhost:8000/v1/chat/completions  # qwen3.8-flash-next
export Q27_URL=http://localhost:8001/v1/chat/completions    # Qwen/Qwen3.8-27B
python3 lab.py run --lanes gemini --cells clean,selfcond_silent --seeds 1
python3 lab.py summary
```

`run_all.sh` runs all 13 setups × 5 seeds × 3 lanes (195 runs). A finished run is skipped when its result file exists. Set `CFL_RESULTS=<dir>` to write the results somewhere else.

## Sources

- Chroma, [Context Rot](https://research.trychroma.com/context-rot) (Jul 2025)
- Drew Breunig, [How Long Contexts Fail](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html) (Jun 2025)
- Sinha et al., [The Illusion of Diminishing Returns](https://arxiv.org/abs/2509.09677) (self-conditioning, Sep 2025)
- Laban et al., [LLMs Get Lost in Multi-Turn Conversation](https://arxiv.org/abs/2505.06120) (May 2025)
- Paramanayakam et al., [Less is More](https://arxiv.org/abs/2411.15399) (the 46-vs-19 tools example, Nov 2024)
