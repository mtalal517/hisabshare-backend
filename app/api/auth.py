from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import uuid4
import random

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse


router = APIRouter(prefix="/auth", tags=["auth"])


def pin_is_taken(pin: str, users: list[User]) -> bool:
    return any(verify_password(pin, user.password_hash) for user in users)


def generate_pin_suggestions(users: list[User], count: int = 3) -> list[str]:
    suggestions: list[str] = []
    while len(suggestions) < count:
        pin = f"{random.randint(0, 999999):06d}"
        if pin not in suggestions and not pin_is_taken(pin, users):
            suggestions.append(pin)
    return suggestions


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    users = db.scalars(select(User)).all()
    if pin_is_taken(payload.pin, users):
        raise HTTPException(
            status_code=409,
            detail={
                "message": "PIN already taken",
                "suggested_pins": generate_pin_suggestions(users),
            },
        )

    user = User(
        name=payload.name,
        email=f"{uuid4()}@example.com",
        password_hash=hash_password(payload.pin),
        preferred_language=payload.preferred_language,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    users = db.scalars(select(User)).all()
    user = next((candidate for candidate in users if verify_password(payload.pin, candidate.password_hash)), None)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid PIN")
    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
