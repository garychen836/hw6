"""Turn output/cache_test.json into output/cache_test.md."""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
data = json.loads((ROOT / "output" / "cache_test.json").read_text())
rows = data["calls"]
HB = 10058  # handbook tokens from handbook_estimate.md
P = json.loads((ROOT / "data" / "prices.json").read_text())["gpt-6-luna"]


def agg(setup):
    sel = [r for r in rows if r["setup"] == setup]
    docs = defaultdict(float)
    for r in sel:
        docs[r["doc"]] += r["cost_usd"]
    tot = lambda k: sum(r[k] for r in sel)
    return {"calls": len(sel), "in": tot("input_tokens"), "cached": tot("cached_tokens"),
            "out": tot("output_tokens"), "cost": tot("cost_usd"), "docs": dict(docs)}


on, off, warm = agg("cache_on"), agg("cache_off"), agg("warmup")
n = len(on["docs"])
per_on, per_off = on["cost"] / n, off["cost"] / n
saved = 1 - on["cost"] / off["cost"]
req1 = [r for r in rows if r["setup"] == "cache_off" and r["request_index"] == 1]
req1_in = sum(r["input_tokens"] for r in req1) / len(req1)
req2 = [r for r in rows if r["setup"] == "cache_off" and r["request_index"] == 2]
req2_in = sum(r["input_tokens"] for r in req2) / len(req2)
req1_on = [r for r in rows if r["setup"] == "cache_on" and r["request_index"] == 1]
req2_on = [r for r in rows if r["setup"] == "cache_on" and r["request_index"] == 2]
hit = lambda rs: sum(r["cached_tokens"] for r in rs) / sum(r["input_tokens"] for r in rs)
out_cost_on = on["out"] * P["output_per_1m"] / 1e6
unc_in_on = (on["in"] - on["cached"]) * P["input_per_1m"] / 1e6
cached_in_on = on["cached"] * P["cached_input_per_1m"] / 1e6
est_unc = HB * P["input_per_1m"] / 1e6
est_cac = HB * P["cached_input_per_1m"] / 1e6
days = 1000 * 30

md = f"""# Cache test (Problem 4)

Setup: baseline agent, 12 practice docs, model gpt-6-luna, API path `{data['api_path']}`. Every model request is in `cache_test.json` (setup, doc, request index, input / cached / output tokens, cost). Prices from `data/prices.json`: input $0.10, cached input $0.01, output $0.50 per 1M tokens.

- Cache ON: identical system prompt (handbook first, then instructions) and a fixed `prompt_cache_key`.
- Cache OFF: a fresh random id on the very first line of the system prompt, regenerated before **every** request (a per-run id is not enough: the second request of a run, after the tool call, would otherwise match the first one's prefix).
- Check: cached_tokens == 0 on all {off['calls']} cache-OFF requests: **{data['cache_off_all_zero']}**.
- Warm-up: one extra call on p01 before the ON set ({warm['calls']} requests, ${warm['cost']:.6f}, {warm['cached']:,} cached tokens), reported separately and not in the totals. It was already cache-warm from earlier runs of the same prefix, so it did not show a cold start. The truly cold call (the first one ever made with this prefix) is not in this file.

## Totals
| Setup | Requests | Input tokens | Cached tokens | Output tokens | Total cost (12 docs) | Cost per doc |
|---|---|---|---|---|---|---|
| Cache ON | {on['calls']} | {on['in']:,} | {on['cached']:,} ({on['cached'] / on['in']:.1%}) | {on['out']:,} | ${on['cost']:.6f} | ${per_on:.6f} |
| Cache OFF | {off['calls']} | {off['in']:,} | {off['cached']:,} | {off['out']:,} | ${off['cost']:.6f} | ${per_off:.6f} |

**Saved by caching: {saved:.1%}** (${off['cost'] - on['cost']:.6f} over 12 docs, ${per_off - per_on:.6f} per doc).

Per doc:

| Doc | ON | OFF |
|---|---|---|
""" + "\n".join(f"| {d} | ${on['docs'][d]:.6f} | ${off['docs'][d]:.6f} |" for d in sorted(on["docs"])) + f"""

## Comparison with the Problem 2 estimate
- Estimate (handbook only, one request): uncached ${est_unc:.6f}, cached ${est_cac:.7f}, a 90% saving.
- Real run, per request, cache OFF: first request averages {req1_in:,.0f} input tokens, second {req2_in:,.0f}. That is {HB:,} handbook tokens + about 280 for the instructions (tiktoken on `prompt_baseline.md`) + roughly 350 for the tool definitions, the user message and chat-format overhead = about {req1_in:,.0f}. The second request adds about {req2_in - req1_in:,.0f} tokens for the tool call and the document text. So the API count is consistent with the tiktoken handbook count.
- A whole doc is two requests, so the handbook is paid twice: the "per doc" input is about {2 * HB:,} tokens of handbook, double the one-call estimate. The estimate doubled would be ${2 * est_unc:.6f} uncached and ${2 * est_cac:.6f} cached; the measured per-doc totals are ${per_off:.6f} and ${per_on:.6f}, the rest being the extra prompt/doc tokens and the output tokens.
- Saving: the estimate says 90% on the handbook alone; the measured saving is {saved:.1%}. It is lower because output tokens are never discounted and a small part of each prompt is not cached.

## Projection: 1,000 docs/day x 30 days = {days:,} docs
| Setup | Cost per doc | Per day | Per 30 days |
|---|---|---|---|
| Cache ON | ${per_on:.6f} | ${per_on * 1000:.2f} | ${per_on * days:.2f} |
| Cache OFF | ${per_off:.6f} | ${per_off * 1000:.2f} | ${per_off * days:.2f} |
| Difference | | ${(per_off - per_on) * 1000:.2f} | ${(per_off - per_on) * days:.2f} |

## Surprises and why
1. **Two requests per document.** The agent calls `read_document`, so each doc is one request that asks for the tool and a second that returns the answer. The whole prompt, handbook included, is sent twice. Caching matters even more for this reason: the second request's handbook is always a cache hit once the first has run.
2. **Even at a 90% discount the handbook is still the biggest cost.** Output costs 5x input per 1M ($0.50 vs $0.10). With caching on the ${on['cost']:.6f} total splits into cached input ${cached_in_on:.6f} ({cached_in_on / on['cost']:.0%}), output ${out_cost_on:.6f} ({out_cost_on / on['cost']:.0%}) and uncached input ${unc_in_on:.6f} ({unc_in_on / on['cost']:.0%}). Output is only about {on['out'] / on['calls']:.0f} tokens per request, but it is never discounted, so it is a large share of what is left; and the handbook is sent twice per doc, so the cached input line is still the largest.
3. **Cache hit rate is high but not 100%.** With caching on, {hit(req1_on):.1%} of request-1 input and {hit(req2_on):.1%} of request-2 input was cached. OpenAI caches whole prefix blocks (starts at 1,024 tokens, then in 128-token steps), so the tail of the prompt is billed at full price: the end of the instructions, the user message with the doc path, and the tool result. The document text sits last, so it is never cached.
4. **Cached counts vary a little between identical prefixes** (about 10,100 to 10,700 per request), because cache routing and block granularity are not exact. The saving is therefore close to, but not exactly, the ideal 90%.
5. **The first call ever is not cached.** Any new prefix is billed at the full input price once. Here the warm-up was already warm, so a cold start is not visible in the numbers.
6. **No cache-write charge.** OpenAI reports no cache-write tokens, so the $0.125 cache-write price applies to 0 tokens.
"""
(ROOT / "output" / "cache_test.md").write_text(md)
print(md[:2500])
