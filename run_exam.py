"""Problem 8: final defended agent (default configuration) on the 10 exam documents."""
import asyncio
import json
import shutil
from pathlib import Path

import agent

ROOT = Path(__file__).parent
OUT = ROOT / "output"


async def main():
    trap_path = OUT / "trap_calls.json"
    shutil.copy(trap_path, OUT / "trap_calls_before_exam.json")  # keep what was there
    trap_path.write_text("[]")
    client, _ = await agent.pick_client()
    results = []
    for f in sorted(p.name for p in (ROOT / "data" / "exam_docs").iterdir()):
        before = len(json.loads(trap_path.read_text()))
        out = await agent.run_doc(f"data/exam_docs/{f}", "defended", True, client)
        a, u = out["answer"], out["usage"]
        traps = json.loads(trap_path.read_text())[before:]
        results.append({"file": f, "vendor": a["vendor"], "sku": a["sku"], "unit_price": a["unit_price"],
                        "lead_time_days": a["lead_time_days"], "min_order": a["min_order"], "decision": a["decision"],
                        "reason": a["reason"], "trap_tool_called": bool(traps), "input_tokens": u["input_tokens"],
                        "cached_tokens": u["cached_tokens"], "output_tokens": u["output_tokens"], "cost_usd": u["cost_usd"]})
        print(f, a["decision"], a["unit_price"], flush=True)
    (OUT / "exam_results.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
