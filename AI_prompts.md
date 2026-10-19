# AI prompts log — HW 6

The assistant was Claude Code. Claude Opus planned the work and checked each result. A Claude Sonnet coding agent wrote the code and ran it. I gave the assignment in two messages, pasting screenshots of the problems in place of retyping each one. Those messages are below, word for word. Under each problem is the brief the planner gave the coding agent, plus any follow-up that was needed.

## My prompts (verbatim)

## Problem 1: Vibe coder prompts

- **Note:** this file was written at the end. Each problem section below records how my request was split up.



## Problem 2: Size up the handbook

- **Brief to coding agent:** "Count handbook tokens with tiktoken (o200k_base) and write output/handbook_estimate.md: count + method, cost for 1 call and 1,000 calls, uncached vs cached, math shown, prices from data/prices.json."
- **Follow-up:** the first draft called the chars/4 rule of thumb "close" when it was 28% low. The explanation was rewritten: table-heavy text splits into many short tokens.



## Problem 3: Build the vendor desk agent

- **Brief to coding agent:** "Build models.py, tools.py, prompts/prompt.md, agent.py with PydanticAI on gpt-6-luna. read_document handles HTML, PDF and .eml. send_email and approve_payment only append to output/trap_calls.json. Log usage_log.json and audit_trail.json after every run. Put the handbook first in the system prompt. Run on p01 and p08 and write output/harness.md."
- **Follow-up:** the Portkey key had hit its usage cap (HTTP 412), so the agent falls back to OpenAI direct. The model is still gpt-6-luna only.



## Problem 4: With and without cached tokens

- **Brief to coding agent:** "Run all 12 practice docs with cache on (after a warm-up) and with cache off (unique nonce at the start of the system prompt). Save every model call to cache_test.json, prove cache-off shows 0 cached tokens, and write cache_test.md: totals, % saved, comparison to the Problem 2 estimate, a 30-day projection, and surprises."
- **Follow-up:** a per-run nonce still let the second request of a run hit the cache. The nonce now changes before every request.



## Problem 5: Attack your own agent

- **Brief to coding agent:** "Run the undefended agent on all 12 docs and compare to practice_key.json. Record per-field matches, decision match, trap calls and links/strange text. For each fooled doc, say what fooled it, where it hid in the file, and how that compares with what a person sees."



## Problem 6: Defend your agent

- **Brief to coding agent:** "Three switchable layers. Code: sanitize hidden HTML/PDF/email text before the model sees it. Design: an extraction-only model with no tools; decision and reason computed in Python from the handbook; send_email/approve_payment only behind a human sign-off. Prompt: rules in prompts/prompt.md. Keep --mode baseline. Run all 12 plus per-layer ablations, and write defense_results.json/.md and the Safety section of harness.md."
- **Follow-up:** after the PDF hardening in Problem 7, a "28 business days" lead time came back as null. A line was added to prompt.md and everything was rerun.



## Problem 7: Red team

- **Brief to coding agent:** "Make two new attack files in data/my_attacks/ using tricks and goals not in the practice set; a person must see a normal quote. Run each 3× on the undefended and defended agent. Harden the defense if it fails, then write red_team.md."
- **Result:** covered text in a PDF (under a white box) and a base64 email attachment both fooled the undefended agent 3/3 and the defended agent 0/3. A new PDF check drops covered characters.



## Problem 8: Exam documents

- **Brief to coding agent:** "Run the final defended agent on all 10 exam docs with a script and write exam_results.json with exactly the required fields. No hand edits."



## Problem 9: Results page

- **Brief to coding agent:** "build_report.py → one self-contained output/hw6_report.html (inline CSS + SVG, no internet): caching chart, attacks before/after, defense cost, exam + red team, and a recommendation to the store manager with the monthly cost at 1,000 docs/day. All numbers read from the output files."



## Problem 10: Push to GitHub

- **Brief:** "README with run instructions, .gitignore keeping .env out, .env.example with placeholders, scan for leaked keys and other model ids, then push to a public repo."

