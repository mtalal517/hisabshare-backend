from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class HisabCreate(BaseModel):
    person_name: str = Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=255)


class HisabUpdate(BaseModel):
    person_name: str | None = Field(default=None, min_length=1, max_length=255)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    status: str | None = Field(default=None, max_length=20)


class HisabResponse(BaseModel):
    id: str
    person_name: str
    title: str
    total_amount: Decimal
    share_token: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ShareResponse(BaseModel):
    share_url: str
    share_token: str

