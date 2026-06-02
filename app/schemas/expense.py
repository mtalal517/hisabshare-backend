from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    hisab_id: str
    item_name: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(gt=0)
    receipt_url: str | None = None


class ExpenseUpdate(BaseModel):
    item_name: str | None = Field(default=None, min_length=1, max_length=255)
    amount: Decimal | None = Field(default=None, gt=0)
    receipt_url: str | None = None


class ExpenseResponse(BaseModel):
    id: str
    hisab_id: str
    item_name: str
    amount: Decimal
    receipt_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

