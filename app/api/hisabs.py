from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.models import Hisab, User
from app.schemas.hisab import HisabCreate, HisabResponse, HisabUpdate, ShareResponse


router = APIRouter(prefix="/hisabs", tags=["hisabs"])


@router.post("", response_model=HisabResponse, status_code=status.HTTP_201_CREATED)
def create_hisab(payload: HisabCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    hisab = Hisab(user_id=user.id, person_name=payload.person_name, title=payload.title)
    db.add(hisab)
    db.commit()
    db.refresh(hisab)
    return hisab


@router.get("", response_model=list[HisabResponse])
def list_hisabs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(select(Hisab).where(Hisab.user_id == user.id).order_by(Hisab.created_at.desc())).all()


@router.get("/{hisab_id}", response_model=HisabResponse)
def get_hisab(hisab_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    hisab = db.scalar(select(Hisab).where(Hisab.id == hisab_id, Hisab.user_id == user.id))
    if not hisab:
        raise HTTPException(status_code=404, detail="Hisab not found")
    return hisab


@router.put("/{hisab_id}", response_model=HisabResponse)
def update_hisab(
    hisab_id: str,
    payload: HisabUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    hisab = db.scalar(select(Hisab).where(Hisab.id == hisab_id, Hisab.user_id == user.id))
    if not hisab:
        raise HTTPException(status_code=404, detail="Hisab not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(hisab, field, value)
    db.commit()
    db.refresh(hisab)
    return hisab


@router.delete("/{hisab_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hisab(hisab_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    hisab = db.scalar(select(Hisab).where(Hisab.id == hisab_id, Hisab.user_id == user.id))
    if not hisab:
        raise HTTPException(status_code=404, detail="Hisab not found")
    db.delete(hisab)
    db.commit()


@router.post("/{hisab_id}/share", response_model=ShareResponse)
def generate_share_link(hisab_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    hisab = db.scalar(select(Hisab).where(Hisab.id == hisab_id, Hisab.user_id == user.id))
    if not hisab:
        raise HTTPException(status_code=404, detail="Hisab not found")
    settings = get_settings()
    return ShareResponse(
        share_token=hisab.share_token,
        share_url=f"{settings.frontend_url}/share/{hisab.share_token}",
    )

