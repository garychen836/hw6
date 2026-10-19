"""Problem 4: all 12 practice docs with and without prompt caching; every model call is logged."""
import asyncio
import json
from pathlib import Path

import agent
import tools
from tools import cost_usd

ROOT = Path(__file__).parent
DOCS = sorted((ROOT / "data" / "practice_docs").iterdir())


async def run_set(setup: str, cache: bool, client, rows: list) -> None:
    for d in DOCS:
        rel = str(d.relative_to(ROOT))
        out = await agent.run_doc(rel, "baseline", cache, client)
        for i, c in enumerate(out["calls"], 1):
            rows.append({"setup": setup, "doc": d.name, "request_index": i, **c,
                         "cost_usd": round(c["cost_usd"], 8)})
        print(setup, d.name, out["usage"]["input_tokens"], out["usage"]["cached_tokens"])


async def main() -> None:
    client, path = await agent.pick_client()
    rows: list = []
    # one warm-up call so the first measured doc is not paying for a cold cache
    await run_set_warm(client, rows)
    await run_set("cache_on", True, client, rows)
    await run_set("cache_off", False, client, rows)
    bad = [r for r in rows if r["setup"] == "cache_off" and r["cached_tokens"] != 0]
    (ROOT / "output" / "cache_test.json").write_text(json.dumps(
        {"api_path": path, "cache_off_all_zero": not bad, "calls": rows}, indent=2))
    print("api path:", path, "| cache-off calls with cached tokens:", len(bad))


async def run_set_warm(client, rows):
    out = await agent.run_doc(str((DOCS[0]).relative_to(ROOT)), "baseline", True, client)
    for i, c in enumerate(out["calls"], 1):
        rows.append({"setup": "warmup", "doc": DOCS[0].name, "request_index": i, **c})
    print("warmup done")


if __name__ == "__main__":
    asyncio.run(main())
