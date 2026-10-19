# HW 6: Vendor desk agent for Campus Customs

An AI agent that reads a vendor document (HTML quote, PDF quote or email), pulls out the vendor, SKU, unit price,
lead time and minimum order, and recommends or rejects the vendor using the shop handbook rules. The project
measures what it costs (prompt caching), shows how a plain agent is fooled by hidden text in documents, and adds
three defense layers. The only model used is `gpt-6-luna`.

## Setup
```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env      # then fill in your own keys
```
`.env` needs `PORTKEY_API_KEY` and `PORTKEY_BASE_URL` (tried first) and `OPENAI_API_KEY`. If Portkey refuses a
call (for example its usage limit is reached), the agent falls back to OpenAI directly. The choice is made once per
run; set `API_PATH=openai` to skip the Portkey probe. This project's runs used the OpenAI-direct path because
the Portkey key was capped. Keys are never printed or logged.

## Run the agent
```
.venv/bin/python agent.py --doc data/practice_docs/p01_bluehen_quote.html                # full defense (default)
.venv/bin/python agent.py --doc ... --mode baseline                                       # no defenses
.venv/bin/python agent.py --doc ... --layers code,prompt                                  # choose layers: code, design, prompt
.venv/bin/python agent.py --doc ... --cache off                                           # no prompt caching
```
The two risky tools (`send_email`, `approve_payment`) never send or pay anything; they only write to
`output/trap_calls.json`. In the defended flow they can only be reached by a person at a terminal:
`python agent.py --approve-action email --to ... --subject ... --body ...` or `--approve-action payment --vendor ... --amount ... --reason ...` (typed "yes" required).

## Scripts in problem order
| Problem | Script | Writes |
|---|---|---|
| 2 Handbook cost estimate | `estimate_handbook.py` | `output/handbook_estimate.md` |
| 3 Agent harness | `agent.py`, `models.py`, `tools.py`, `prompts/` | `output/harness.md`, `usage_log.json`, `audit_trail.json`, `trap_calls.json` |
| 4 Caching test | `cache_test.py`, then `cache_report.py` | `output/cache_test.json`, `cache_test.md` |
| 5 Attacks on the baseline | `eval_baseline.py`, then `attack_report.py` | `output/attack_results.json`, `attack_results.md` |
| 6 Defenses and ablations | `eval_defense.py`, then `defense_report.py` | `output/defense_results.json`, `defense_results.md` |
| 7 Red team | `make_attacks.py`, `eval_redteam.py`, `eval_redteam_ablation.py`, `red_team_report.py` | `data/my_attacks/`, `output/red_team_runs_*.json`, `red_team_ablation_a.json`, `red_team.md` |
| 8 Exam | `run_exam.py` | `output/exam_results.json` |
| 9 Report | `build_report.py` (no model calls) | `output/hw6_report.html` |

Results files are produced by these scripts, not edited by hand. Each batch script resets or snapshots the trap log first
(`trap_calls_before_p5.json`, `trap_calls_after_p5.json`, `trap_calls_before_exam.json`).

## File map
- `agent.py`: command line entry point, baseline tool agent, extraction-only agent, human sign-off path.
- `tools.py`: document readers (raw and sanitized), sanitizer, trap tools, audit and usage logging, cost function.
- `rules.py`: handbook sections 4, 5, 6 and 9 as code; computes the decision and reason.
- `models.py`: Pydantic types (`VendorFacts`, `VendorDecision`, usage records).
- `prompts/prompt.md` (defended instructions) and `prompts/prompt_baseline.md` (baseline instructions).
- `data/`: handbook, prices, practice and exam documents, `practice_key.json`, `my_attacks/`.
- `output/`: all results (see the table above) plus `harness.md`, which explains the design and the safety layers.
- `output/hw6_report.html`: the one-file report (open it in a browser, works offline).

## The three defense layers (details in `output/harness.md`)
1. Code: a sanitizer keeps only text a person would see (hidden HTML, invisible or covered PDF text, email attachments and unseen parts are dropped).
2. Design: the model that reads the document has no tools and only returns facts; the decision and reason are computed in Python from the handbook.
3. Prompt: instructions that document text is data, not commands.
