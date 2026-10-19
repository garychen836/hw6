"""The handbook purchasing rules as code: the decision and the reason are computed here, not by the model."""
import re
from functools import lru_cache
from pathlib import Path

from models import VendorFacts

HANDBOOK = Path(__file__).parent / "data" / "shop_handbook.md"
MAX_LEAD_DAYS = 21
MAX_MIN_ORDER = 600


def norm(s: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _section(text: str, number: int) -> list[list[str]]:
    m = re.search(rf"^## {number}\. .*?$(.*?)(?=^## \d+\. |\Z)", text, flags=re.S | re.M)
    rows = []
    for line in (m.group(1) if m else "").splitlines():
        if line.startswith("|") and not re.match(r"\|[-| ]+\|$", line):
            rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows[1:]  # drop the header row


@lru_cache(maxsize=1)
def load() -> dict:
    text = HANDBOOK.read_text()
    approved = {r[1] for r in _section(text, 5)}
    removed = {r[0] for r in _section(text, 6)}
    catalogue = {r[0]: float(r[4].lstrip("$").replace(",", "")) for r in _section(text, 9)}
    return {"approved": approved, "removed": removed, "catalogue": catalogue}


def match_vendor(name: str | None, names: set[str]) -> str | None:
    """Canonical handbook name for a vendor string, or None."""
    n = norm(name)
    if not n:
        return None
    for c in names:
        if norm(c) == n:
            return c
    for c in names:  # e.g. "Blue Hen Apparel Inc."
        if len(n) >= 6 and (norm(c) in n or n in norm(c)):
            return c
    return None


def decide(f: VendorFacts) -> tuple[str, str]:
    """Return (decision, one-sentence reason) from the four purchasing checks in handbook section 4."""
    r = load()
    if match_vendor(f.vendor, r["removed"]):
        return "do_not_recommend", "The vendor is on the removed or pending vendor list (handbook section 6), so it is never recommended."
    if not match_vendor(f.vendor, r["approved"]):
        return "do_not_recommend", "The approved-vendor check fails: the vendor is not on the approved vendor list (handbook section 5)."
    cap = r["catalogue"].get(f.sku or "")
    if f.unit_price is None:
        return "do_not_recommend", "The price check fails: the document does not state a unit price."
    if cap is None:
        return "do_not_recommend", "The price check fails: the SKU is missing or has no max unit cost in the catalogue."
    if f.unit_price > cap + 1e-9:
        return "do_not_recommend", f"The price check fails: ${f.unit_price:.2f} is above the max unit cost of ${cap:.2f} for {f.sku}."
    if f.lead_time_days is None:
        return "do_not_recommend", "The lead-time check fails: the document does not state a lead time."
    if f.lead_time_days > MAX_LEAD_DAYS:
        return "do_not_recommend", f"The lead-time check fails: {f.lead_time_days} days is more than the {MAX_LEAD_DAYS}-day limit."
    if f.min_order is None:
        return "do_not_recommend", "The minimum-order check fails: the document does not state a minimum order."
    if f.min_order > MAX_MIN_ORDER:
        return "do_not_recommend", f"The minimum-order check fails: {f.min_order} units is more than the {MAX_MIN_ORDER}-unit limit."
    return ("recommend", f"All four checks pass: approved vendor, ${f.unit_price:.2f} is at or below the ${cap:.2f} max unit cost, "
            f"{f.lead_time_days}-day lead time is within {MAX_LEAD_DAYS} days, and the {f.min_order}-unit minimum order is within {MAX_MIN_ORDER}.")
