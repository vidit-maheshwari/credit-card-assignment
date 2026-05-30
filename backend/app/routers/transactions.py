from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models.dto import TransactionOut
from app.services.analytics import get_transactions

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.get("/")
def list_transactions(
    month: Optional[str] = Query(None, description="Filter by month (YYYY-MM)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    bank: Optional[str] = Query(None, description="Filter by bank"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get transactions with optional filters."""
    result = get_transactions(db, month=month, category=category, bank=bank, limit=limit, offset=offset)
    return {
        "total": result["total"],
        "transactions": [TransactionOut.model_validate(t) for t in result["transactions"]],
    }
