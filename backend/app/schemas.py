"""Public typed API contracts for the first vertical slice."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

DocType = Literal["claim_form", "police_report", "repair_estimate", "policy_excerpt", "other"]


class ClaimCreate(BaseModel):
    claimant_label: str = Field(min_length=2, max_length=100)
    policy_ref: str = Field(pattern=r"^SYN-[A-Z0-9-]{3,32}$")
    incident_date: date

    model_config = ConfigDict(extra="forbid")


class DocumentCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=150)
    document_type: DocType
    text: str = Field(min_length=1, max_length=50000)

    model_config = ConfigDict(extra="forbid")


class ReviewCreate(BaseModel):
    note: str = Field(min_length=10, max_length=2000)

    model_config = ConfigDict(extra="forbid")
