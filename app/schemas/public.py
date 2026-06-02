from app.schemas.expense import ExpenseResponse
from app.schemas.hisab import HisabResponse


class PublicBillResponse(HisabResponse):
    expenses: list[ExpenseResponse]

