# Cache test (Problem 4)

Setup: baseline agent, 12 practice docs, model gpt-6-luna, API path `openai`. Every model request is in `cache_test.json` (setup, doc, request index, input / cached / output tokens, cost). Prices from `data/prices.json`: input $0.10, cached input $0.01, output $0.50 per 1M tokens.

- Cache ON: identical system prompt (handbook first, then instructions) and a fixed `prompt_cache_key`.
- Cache OFF: a fresh random id on the very first line of the system prompt, regenerated before **every** request (a per-run id is not enough: the second request of a run, after the tool call, would otherwise match the first one's prefix).
- Check: cached_tokens == 0 on all 24 cache-OFF requests: **True**.
- Warm-up: one extra call on p01 before the ON set (2 requests, $0.000299, 21,276 cached tokens), reported separately and not in the totals. It was already cache-warm from earlier runs of the same prefix, so it did not show a cold start. The truly cold call (the first one ever made with this prefix) is not in this file.

## Totals
| Setup | Requests | Input tokens | Cached tokens | Output tokens | Total cost (12 docs) | Cost per doc |
|---|---|---|---|---|---|---|
| Cache ON | 24 | 258,428 | 253,780 (98.2%) | 1,424 | $0.003715 | $0.000310 |
| Cache OFF | 24 | 259,077 | 0 | 1,435 | $0.026625 | $0.002219 |

**Saved by caching: 86.0%** ($0.022911 over 12 docs, $0.001909 per doc).

Per doc:

| Doc | ON | OFF |
|---|---|---|
| p01_bluehen_quote.html | $0.000307 | $0.002213 |
| p02_elmcity_quote.html | $0.000314 | $0.002219 |
| p03_ivyprint_catalog.html | $0.000309 | $0.002212 |
| p04_harborstitch_quote.html | $0.000318 | $0.002226 |
| p05_maplemills_quote.pdf | $0.000289 | $0.002209 |
| p06_qtextile_quote.pdf | $0.000310 | $0.002220 |
| p07_longwharf_quote.pdf | $0.000307 | $0.002224 |
| p08_chapelst_email.eml | $0.000307 | $0.002214 |
| p09_westville_email.eml | $0.000317 | $0.002224 |
| p10_eastrock_email.eml | $0.000318 | $0.002227 |
| p11_yorkst_quote.html | $0.000306 | $0.002211 |
| p12_bluehen_quote.pdf | $0.000311 | $0.002226 |

## Comparison with the Problem 2 estimate
- Estimate (handbook only, one request): uncached $0.001006, cached $0.0001006, a 90% saving.
- Real run, per request, cache OFF: first request averages 10,718 input tokens, second 10,871. That is 10,058 handbook tokens + about 280 for the instructions (tiktoken on `prompt_baseline.md`) + roughly 350 for the tool definitions, the user message and chat-format overhead = about 10,718. The second request adds about 153 tokens for the tool call and the document text. So the API count is consistent with the tiktoken handbook count.
- A whole doc is two requests, so the handbook is paid twice: the "per doc" input is about 20,116 tokens of handbook, double the one-call estimate. The estimate doubled would be $0.002012 uncached and $0.000201 cached; the measured per-doc totals are $0.002219 and $0.000310, the rest being the extra prompt/doc tokens and the output tokens.
- Saving: the estimate says 90% on the handbook alone; the measured saving is 86.0%. It is lower because output tokens are never discounted and a small part of each prompt is not cached.

## Projection: 1,000 docs/day x 30 days = 30,000 docs
| Setup | Cost per doc | Per day | Per 30 days |
|---|---|---|---|
| Cache ON | $0.000310 | $0.31 | $9.29 |
| Cache OFF | $0.002219 | $2.22 | $66.56 |
| Difference | | $1.91 | $57.28 |

## Surprises and why
1. **Two requests per document.** The agent calls `read_document`, so each doc is one request that asks for the tool and a second that returns the answer. The whole prompt, handbook included, is sent twice. Caching matters even more for this reason: the second request's handbook is always a cache hit once the first has run.
2. **Even at a 90% discount the handbook is still the biggest cost.** Output costs 5x input per 1M ($0.50 vs $0.10). With caching on the $0.003715 total splits into cached input $0.002538 (68%), output $0.000712 (19%) and uncached input $0.000465 (13%). Output is only about 59 tokens per request, but it is never discounted, so it is a large share of what is left; and the handbook is sent twice per doc, so the cached input line is still the largest.
3. **Cache hit rate is high but not 100%.** With caching on, 98.7% of request-1 input and 97.7% of request-2 input was cached. OpenAI caches whole prefix blocks (starts at 1,024 tokens, then in 128-token steps), so the tail of the prompt is billed at full price: the end of the instructions, the user message with the doc path, and the tool result. The document text sits last, so it is never cached.
4. **Cached counts vary a little between identical prefixes** (about 10,100 to 10,700 per request), because cache routing and block granularity are not exact. The saving is therefore close to, but not exactly, the ideal 90%.
5. **The first call ever is not cached.** Any new prefix is billed at the full input price once. Here the warm-up was already warm, so a cold start is not visible in the numbers.
6. **No cache-write charge.** OpenAI reports no cache-write tokens, so the $0.125 cache-write price applies to 0 tokens.
