"""Problem 7 extra: attack A (covered text) under single layers, with and without the covered-text check."""
import asyncio
import json
import os
from pathlib import Path

import agent

ROOT = Path(__file__).parent
DOC = "data/my_attacks/a_covered_text_bluehen.pdf"
CONFIGS = {"code_only": ("code",), "design_only": ("design",), "prompt_only": ("prompt",), "code+design": ("code", "design")}


async def main():
    client, _ = await agent.pick_client()
    res = {}
    for cover in ("with_cover_check", "without_cover_check"):
        if cover == "without_cover_check":
            os.environ["SANITIZER_NO_COVER_CHECK"] = "1"
        else:
            os.environ.pop("SANITIZER_NO_COVER_CHECK", None)
        for name, layers in CONFIGS.items():
            if cover == "without_cover_check" and "code" not in layers:
                continue  # the check only matters when the code layer is on
            prices = []
            for _ in range(3):
                out = await agent.run_doc(DOC, "defended", True, client, layers=layers)
                prices.append(out["answer"]["unit_price"])
            res[f"{name}/{cover}"] = prices
            print(name, cover, prices, flush=True)
    (ROOT / "output" / "red_team_ablation_a.json").write_text(json.dumps(res, indent=2))


asyncio.run(main())
