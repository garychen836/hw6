# Handbook cost estimate (Problem 2)

## Size of the handbook
- File: `data/shop_handbook.md`, 28,903 characters.
- Method: tiktoken with the `o200k_base` encoding, `len(enc.encode(text))` = **10,058 tokens**.
- Sanity check: characters / 4 = 7,226 tokens (-28.2% vs tiktoken). The rule of thumb undercounts here because most of the handbook is tables full of SKUs, prices, pipes and dashes, which split into many short tokens; the real API count in Problem 4 confirms the tiktoken figure.

## Prices (from `data/prices.json`, per 1M tokens)
| Input | Cached input | Cache write | Output |
|---|---|---|---|
| $0.1 | $0.01 | $0.125 | $0.5 |

OpenAI reports no cache-write tokens, so the cache-write price applies to 0 tokens in this project. It is shown below only for reference.

## Handbook alone, input cost only
Formula: tokens x price_per_1M / 1,000,000.

| Case | 1 call | 1,000 calls |
|---|---|---|
| Uncached | 10,058 x $0.1 / 1e6 = **$0.001006** | $0.001006 x 1,000 = **$1.0058** |
| Cached (every call hits) | 10,058 x $0.01 / 1e6 = **$0.0001006** | $0.0001006 x 1,000 = **$0.10058** |
| Reference: cache write price | 10,058 x $0.125 / 1e6 = $0.001257 | not charged by OpenAI |

- Saving per call when cached: $0.000905 (90%).
- Saving over 1,000 calls: $0.9052.
- Caveats: the very first call (the warm-up) is uncached, and caching works in 128-token steps after the first 1,024 tokens, so the real cached share is a little below 100%. Output tokens and the document itself are not included here.
