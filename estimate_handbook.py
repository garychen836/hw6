"""Count handbook tokens and write output/handbook_estimate.md."""
import json
from pathlib import Path
import tiktoken

ROOT = Path(__file__).parent
text = (ROOT / "data" / "shop_handbook.md").read_text()
prices = json.loads((ROOT / "data" / "prices.json").read_text())
p = prices["gpt-6-luna"]

enc = tiktoken.get_encoding("o200k_base")
tokens = len(enc.encode(text))
chars = len(text)
approx = chars / 4

unc1 = tokens * p["input_per_1m"] / 1e6
cac1 = tokens * p["cached_input_per_1m"] / 1e6
wr1 = tokens * p["cache_write_per_1m"] / 1e6
n = 1000

md = f"""# Handbook cost estimate (Problem 2)

## Size of the handbook
- File: `data/shop_handbook.md`, {chars:,} characters.
- Method: tiktoken with the `o200k_base` encoding, `len(enc.encode(text))` = **{tokens:,} tokens**.
- Sanity check: characters / 4 = {approx:,.0f} tokens ({(approx - tokens) / tokens:+.1%} vs tiktoken). The rule of thumb undercounts here because most of the handbook is tables full of SKUs, prices, pipes and dashes, which split into many short tokens; the real API count in Problem 4 confirms the tiktoken figure.

## Prices (from `data/prices.json`, per 1M tokens)
| Input | Cached input | Cache write | Output |
|---|---|---|---|
| ${p['input_per_1m']} | ${p['cached_input_per_1m']} | ${p['cache_write_per_1m']} | ${p['output_per_1m']} |

OpenAI reports no cache-write tokens, so the cache-write price applies to 0 tokens in this project. It is shown below only for reference.

## Handbook alone, input cost only
Formula: tokens x price_per_1M / 1,000,000.

| Case | 1 call | 1,000 calls |
|---|---|---|
| Uncached | {tokens:,} x ${p['input_per_1m']} / 1e6 = **${unc1:.6f}** | ${unc1:.6f} x 1,000 = **${unc1 * n:.4f}** |
| Cached (every call hits) | {tokens:,} x ${p['cached_input_per_1m']} / 1e6 = **${cac1:.7f}** | ${cac1:.7f} x 1,000 = **${cac1 * n:.5f}** |
| Reference: cache write price | {tokens:,} x ${p['cache_write_per_1m']} / 1e6 = ${wr1:.6f} | not charged by OpenAI |

- Saving per call when cached: ${unc1 - cac1:.6f} ({1 - cac1 / unc1:.0%}).
- Saving over 1,000 calls: ${(unc1 - cac1) * n:.4f}.
- Caveats: the very first call (the warm-up) is uncached, and caching works in 128-token steps after the first 1,024 tokens, so the real cached share is a little below 100%. Output tokens and the document itself are not included here.
"""
(ROOT / "output" / "handbook_estimate.md").write_text(md)
print(tokens, chars, unc1, cac1)
