from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.models import User


router = APIRouter(prefix="/receipts", tags=["receipts"])
ALLOWED_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_SIZE_BYTES = 10 * 1024 * 1024


@router.post("/upload")
async def upload_receipt(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Receipt must be JPG, PNG, or WEBP")

    content = await file.read()
    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Receipt must be 10 MB or less")

    upload_dir = Path(get_settings().upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{user.id}-{uuid4()}{ALLOWED_TYPES[file.content_type]}"
    path = upload_dir / filename
    path.write_bytes(content)
    return {"receipt_url": f"/uploads/{filename}"}

