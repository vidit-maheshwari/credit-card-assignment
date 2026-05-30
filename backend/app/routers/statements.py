import os
import logging
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.schema import Statement, UserConfig
from app.models.dto import StatementOut, IngestResponse
from app.services.ingestion import ingest_statements, ingest_single_file
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/statements", tags=["Statements"])


class IngestRequest(BaseModel):
    password: Optional[str] = None


class PasswordRequest(BaseModel):
    password: str


class PasswordResponse(BaseModel):
    saved: bool
    password: Optional[str] = None


def _get_saved_password(db: Session) -> Optional[str]:
    config = db.query(UserConfig).filter(UserConfig.key == "pdf_password").first()
    return config.value if config else None


@router.post("/password", response_model=PasswordResponse)
def save_password(body: PasswordRequest, db: Session = Depends(get_db)):
    """Save the PDF statement password."""
    config = db.query(UserConfig).filter(UserConfig.key == "pdf_password").first()
    if config:
        config.value = body.password
    else:
        config = UserConfig(key="pdf_password", value=body.password)
        db.add(config)
    db.commit()
    logger.info("PDF password saved/updated")
    return PasswordResponse(saved=True, password=body.password)


@router.get("/password", response_model=PasswordResponse)
def get_password(db: Session = Depends(get_db)):
    """Get the saved PDF statement password."""
    password = _get_saved_password(db)
    return PasswordResponse(saved=password is not None, password=password)


@router.post("/ingest", response_model=IngestResponse)
def ingest_from_folder(body: IngestRequest = Body(default=IngestRequest()), db: Session = Depends(get_db)):
    """Scan the statements_inbox folder and ingest new files."""
    password = body.password or _get_saved_password(db)
    if not password:
        logger.warning("Ingestion attempted without a saved password")
        raise HTTPException(status_code=400, detail="No password configured. Please save a password first.")
    logger.info("Starting folder ingestion")
    result = ingest_statements(db, password=password)
    logger.info(f"Ingestion complete: {result}")
    return IngestResponse(**result)


@router.post("/upload", response_model=IngestResponse)
async def upload_statement(
    file: UploadFile = File(...),
    password: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Upload and ingest a single statement file."""
    resolved_password = password or _get_saved_password(db)
    if not resolved_password:
        raise HTTPException(status_code=400, detail="No password configured. Please save a password first.")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Save to statements folder
    os.makedirs(settings.STATEMENTS_FOLDER, exist_ok=True)
    filepath = os.path.join(settings.STATEMENTS_FOLDER, file.filename)

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    logger.info(f"Uploaded file: {file.filename}")
    result = ingest_single_file(db, filepath, file.filename, password=resolved_password)
    logger.info(f"Upload ingestion result: {result}")
    return IngestResponse(**result)


@router.get("/", response_model=List[StatementOut])
def list_statements(db: Session = Depends(get_db)):
    """List all imported statements."""
    statements = db.query(Statement).order_by(Statement.imported_at.desc()).all()
    return statements


@router.delete("/{statement_id}")
def delete_statement(statement_id: int, db: Session = Depends(get_db)):
    """Delete a statement and its transactions."""
    statement = db.query(Statement).filter(Statement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    db.delete(statement)
    db.commit()
    return {"message": "Statement deleted successfully"}
