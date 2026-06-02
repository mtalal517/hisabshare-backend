from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import auth, expenses, hisabs, pdf, public, receipts
from app.core.config import get_settings
from app.core.database import Base, engine
from app import models


settings = get_settings()
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HisabShare API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173","https://hisabshare.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

app.include_router(auth.router)
app.include_router(hisabs.router)
app.include_router(expenses.router)
app.include_router(receipts.router)
app.include_router(public.router)
app.include_router(pdf.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
