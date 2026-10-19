"""Pydantic types used by the vendor desk agent."""
from typing import Literal

from pydantic import BaseModel, Field


class VendorFacts(BaseModel):
    """What the document says. Anything the document does not state stays None."""

    vendor: str = Field(description="Vendor name as written in the document")
    sku: str | None = Field(None, description="Campus Customs SKU, e.g. CC-HD-006")
    unit_price: float | None = Field(None, description="Quoted price per unit in dollars")
    lead_time_days: int | None = Field(None, description="Lead time in days")
    min_order: int | None = Field(None, description="Minimum order in units")


class VendorDecision(VendorFacts):
    """Facts plus the purchasing decision and a one-sentence reason."""

    decision: Literal["recommend", "do_not_recommend"]
    reason: str = Field(description="One sentence naming the purchasing check that decided it")


class UsageRecord(BaseModel):
    """One row of usage_log.json (one agent run)."""

    doc: str
    time: str
    mode: str
    cache: str
    input_tokens: int
    cached_tokens: int
    output_tokens: int
    requests: int
    cost_usd: float


class CallRecord(BaseModel):
    """Usage of a single model request inside a run (used for cache tests)."""

    doc: str
    request_index: int
    input_tokens: int
    cached_tokens: int
    output_tokens: int
    cost_usd: float
