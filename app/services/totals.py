from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Expense, Hisab


def refresh_hisab_total(db: Session, hisab_id: str) -> None:
    total = db.scalar(select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.hisab_id == hisab_id))
    hisab = db.get(Hisab, hisab_id)
    if hisab:
        hisab.total_amount = total

