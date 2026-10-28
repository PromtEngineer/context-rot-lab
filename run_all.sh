#!/bin/bash
# Runs all 13 setups x 5 seeds on the three lanes. Needs GEMINI_API_KEY for the gemini lane,
# and FLASH_URL / Q27_URL pointing at OpenAI-compatible servers for the two Qwen lanes.
cd "$(dirname "$0")"
CELLS=clean,poison,poison_validate,clash,clash_prune,distract60,distract160,distract160_compact,tools30,tools100,tools100_search,selfcond_silent,selfcond_feedback
python3 lab.py run --lanes flash,q27,gemini --cells $CELLS --seeds 5 2>&1 | tee -a run_all.log
