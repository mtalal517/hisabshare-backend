from fastapi import HTTPException
from sqlalchemy.exc import OperationalError


def handle_database_error(error: OperationalError) -> None:
    if "database is locked" in str(error).lower():
        raise HTTPException(
            status_code=503,
            detail="Database is busy. Close DB viewers and restart the backend, then try again.",
        ) from error
    raise error

