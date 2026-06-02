from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.models import Hisab
from app.schemas.public import PublicBillResponse


router = APIRouter(tags=["public"])


@router.get("/public/{token}", response_model=PublicBillResponse)
def public_bill(token: str, db: Session = Depends(get_db)):
    hisab = db.scalar(select(Hisab).options(selectinload(Hisab.expenses)).where(Hisab.share_token == token))
    if not hisab:
        raise HTTPException(status_code=404, detail="Bill not found")
    return hisab

