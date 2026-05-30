import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models.dto import MonthlyAnalytics, TrendData
from app.services.analytics import get_monthly_analytics, get_multi_month_trends, get_available_months

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/months")
def available_months(db: Session = Depends(get_db)):
    """Get list of months with available data."""
    months = get_available_months(db)
    return {"months": months}


@router.get("/monthly")
def monthly_analytics(
    month: str = Query(..., description="Month in YYYY-MM format"),
    bank: Optional[str] = Query(None, description="Filter by bank"),
    db: Session = Depends(get_db),
):
    """Get analytics for a specific month."""
    result = get_monthly_analytics(db, month, bank)
    return result


@router.get("/trends")
def trends(
    months: Optional[str] = Query(None, description="Comma-separated months (YYYY-MM). If empty, uses last 6 months."),
    bank: Optional[str] = Query(None, description="Filter by bank"),
    db: Session = Depends(get_db),
):
    """Get multi-month trends."""
    if months:
        month_list = [m.strip() for m in months.split(",")]
    else:
        month_list = get_available_months(db)
        if len(month_list) > 6:
            month_list = month_list[-6:]

    if not month_list:
        return {"months": [], "spend_by_category": {}, "rewards_by_category": {},
                "total_spend_trend": [], "total_rewards_trend": [],
                "mom_spend_change": [], "mom_rewards_change": [],
                "highest_reward_category_trend": []}

    result = get_multi_month_trends(db, month_list, bank)
    return result
