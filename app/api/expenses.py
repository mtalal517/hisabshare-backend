from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.errors import handle_database_error
from app.models import Expense, Hisab, User
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.services.totals import refresh_hisab_total


router = APIRouter(prefix="/expenses", tags=["expenses"])


def require_owned_hisab(db: Session, hisab_id: str, user_id: str) -> Hisab:
    hisab = db.scalar(select(Hisab).where(Hisab.id == hisab_id, Hisab.user_id == user_id))
    if not hisab:
        raise HTTPException(status_code=404, detail="Hisab not found")
    return hisab


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_owned_hisab(db, payload.hisab_id, user.id)
    expense = Expense(**payload.model_dump())
    db.add(expense)
    db.flush()
    refresh_hisab_total(db, payload.hisab_id)
    try:
        db.commit()
    except OperationalError as error:
        handle_database_error(error)
    db.refresh(expense)
    return expense


@router.get("/{hisab_id}", response_model=list[ExpenseResponse])
def list_expenses(hisab_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_owned_hisab(db, hisab_id, user.id)
    return db.scalars(select(Expense).where(Expense.hisab_id == hisab_id).order_by(Expense.created_at.desc())).all()


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: str,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    expense = db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    require_owned_hisab(db, expense.hisab_id, user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    db.flush()
    refresh_hisab_total(db, expense.hisab_id)
    try:
        db.commit()
    except OperationalError as error:
        handle_database_error(error)
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    expense = db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    require_owned_hisab(db, expense.hisab_id, user.id)
    hisab_id = expense.hisab_id
    db.delete(expense)
    db.flush()
    refresh_hisab_total(db, hisab_id)
    try:
        db.commit()
    except OperationalError as error:
        handle_database_error(error)
