from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Hisab, User
from app.services.pdf import build_hisab_pdf


router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.get("/{hisab_id}")
def download_pdf(hisab_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    hisab = db.scalar(
        select(Hisab).options(selectinload(Hisab.expenses)).where(Hisab.id == hisab_id, Hisab.user_id == user.id)
    )
    if not hisab:
        raise HTTPException(status_code=404, detail="Hisab not found")
    return Response(
        content=build_hisab_pdf(hisab),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{hisab.title}.pdf"'},
    )


@router.get("/public/{token}")
def download_public_pdf(token: str, db: Session = Depends(get_db)):
    hisab = db.scalar(select(Hisab).options(selectinload(Hisab.expenses)).where(Hisab.share_token == token))
    if not hisab:
        raise HTTPException(status_code=404, detail="Bill not found")
    return Response(
        content=build_hisab_pdf(hisab),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{hisab.title}.pdf"'},
    )
