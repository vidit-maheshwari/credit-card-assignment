"""
Statement ingestion service.
Handles reading files from the local folder, LLM-based parsing, deduplication, and DB storage.
"""

import os
import hashlib
import logging
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.config import settings
from app.models.schema import Statement, Transaction
from app.services.llm_parser import parse_statement_with_llm

logger = logging.getLogger(__name__)


def compute_file_hash(filepath: str) -> str:
    """Compute SHA256 hash of a file for deduplication."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def _save_parsed_data(db: Session, parsed: dict, filename: str, file_hash: str) -> None:
    """Save LLM-parsed statement data to the database."""
    statement = Statement(
        bank=parsed["bank"],
        card_type=parsed.get("card_type"),
        statement_month=parsed["statement_month"],
        filename=filename,
        file_hash=file_hash,
    )
    db.add(statement)
    db.flush()

    for txn in parsed["transactions"]:
        # Parse transaction date
        txn_date_str = txn.get("transaction_date", "")
        try:
            txn_date = datetime.strptime(txn_date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue  # Skip transactions with invalid dates

        transaction = Transaction(
            statement_id=statement.id,
            transaction_date=txn_date,
            merchant_description=txn.get("merchant_description", "Unknown"),
            amount=float(txn.get("amount", 0)),
            transaction_type=txn.get("transaction_type", "debit"),
            reward_points=float(txn.get("reward_points", 0)),
            category=txn.get("category", "Other"),
            raw_category=None,
        )
        db.add(transaction)

    db.commit()


def ingest_statements(db: Session, password: str = None) -> dict:
    """
    Scan the statements folder and ingest any new files.
    Returns counts of ingested, skipped, and errors.
    """
    folder = settings.STATEMENTS_FOLDER
    logger.info(f"Scanning folder: {folder}")
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        logger.warning("Statements folder did not exist, created it")
        return {"ingested": 0, "skipped": 0, "errors": ["Statements folder was empty. Created folder."]}

    ingested = 0
    skipped = 0
    errors: List[str] = []

    for filename in os.listdir(folder):
        if not filename.lower().endswith(".pdf"):
            continue

        filepath = os.path.join(folder, filename)
        file_hash = compute_file_hash(filepath)

        # Check for duplicates
        existing = db.query(Statement).filter(Statement.file_hash == file_hash).first()
        if existing:
            logger.debug(f"Skipping duplicate: {filename}")
            skipped += 1
            continue

        try:
            logger.info(f"Parsing: {filename}")
            parsed = parse_statement_with_llm(filepath, password=password)
            _save_parsed_data(db, parsed, filename, file_hash)
            logger.info(f"Successfully ingested: {filename}")
            ingested += 1

        except Exception as e:
            db.rollback()
            err_msg = str(e) or f"{type(e).__name__}: {repr(e)}"
            logger.error(f"Failed to ingest {filename}: {err_msg}", exc_info=True)
            errors.append(f"{filename}: {err_msg}")

    logger.info(f"Ingestion summary: ingested={ingested}, skipped={skipped}, errors={len(errors)}")
    return {"ingested": ingested, "skipped": skipped, "errors": errors}


def ingest_single_file(db: Session, filepath: str, filename: str, password: str = None) -> dict:
    """Ingest a single uploaded file."""
    file_hash = compute_file_hash(filepath)

    existing = db.query(Statement).filter(Statement.file_hash == file_hash).first()
    if existing:
        return {"ingested": 0, "skipped": 1, "errors": ["File already imported (duplicate)."]}

    try:
        parsed = parse_statement_with_llm(filepath, password=password)
        _save_parsed_data(db, parsed, filename, file_hash)
        return {"ingested": 1, "skipped": 0, "errors": []}

    except Exception as e:
        db.rollback()
        err_msg = str(e) or f"{type(e).__name__}: {repr(e)}"
        logger.error(f"Failed to ingest single file {filename}: {err_msg}", exc_info=True)
        return {"ingested": 0, "skipped": 0, "errors": [err_msg]}
