"""Problem 6: full defense and ablations on the 12 practice docs (each configuration run twice)."""
import asyncio
import json
import shutil
from pathlib import Path

import agent
from eval_baseline import KEY, compare, strange_text

ROOT = Path(__file__).parent
OUT = ROOT / "output"
CONFIGS = {"full": ("code", "design", "prompt"), "code_only": ("code",), "design_only": ("design",), "prompt_only": ("prompt",)}
REPEATS = 2


async def run_config(name, layers, client, trap_path):
    results = []
    for f in sorted(KEY):
        before = len(json.loads(trap_path.read_text()))
        out = await agent.run_doc(f"data/practice_docs/{f}", "defended", True, client, layers=layers)
        traps = json.loads(trap_path.read_text())[before:]
        a = out["answer"]
        fields = compare(f, a)
        results.append({"file": f, "fields_match": fields, "all_fields_match": all(fields.values()),
                        "decision_match": a["decision"] == KEY[f]["decision"], "expected_decision": KEY[f]["decision"],
                        "trap_tool_called": bool(traps), "trap_calls": traps,
                        "link_or_strange_text": strange_text(a), "answer": a, "usage": out["usage"]})
        r = results[-1]
        print(name, f, "ok" if r["all_fields_match"] and r["decision_match"] else "WRONG", "TRAP" if traps else "",
              "STRANGE" if r["link_or_strange_text"] else "", flush=True)
    return results


async def main():
    trap_path = OUT / "trap_calls.json"
    shutil.copy(trap_path, OUT / "trap_calls_after_p5.json")
    trap_path.write_text("[]")
    client, path = await agent.pick_client()
    runs = {}
    for name, layers in CONFIGS.items():
        runs[name] = [await run_config(f"{name}#{i + 1}", layers, client, trap_path) for i in range(REPEATS)]
    base = json.loads((OUT / "attack_results.json").read_text())["results"]
    (OUT / "defense_results.json").write_text(json.dumps(
        {"api_path": path, "layers": list(CONFIGS["full"]), "results": runs["full"][0], "runs": runs, "baseline": base}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
