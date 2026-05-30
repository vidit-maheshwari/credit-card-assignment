"""
Analytics computation service.
All calculations are deterministic and auditable.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.schema import Transaction, Statement


def get_monthly_analytics(db: Session, month: str, bank: Optional[str] = None) -> dict:
    """
    Compute analytics for a given month (YYYY-MM format).
    All calculations are deterministic.
    """
    query = db.query(Transaction).join(Statement).filter(
        Statement.statement_month == month,
        Transaction.transaction_type == "debit"
    )
    if bank:
        query = query.filter(Statement.bank == bank)

    transactions = query.all()

    if not transactions:
        return {
            "month": month,
            "total_spend": 0.0,
            "total_rewards": 0.0,
            "category_spend": {},
            "category_rewards": {},
            "highest_reward_category": None,
            "highest_reward_rate_category": None,
            "transaction_count": 0,
        }

    # Calculate category-wise spend and rewards
    category_spend = {}
    category_rewards = {}

    for txn in transactions:
        cat = txn.category
        category_spend[cat] = category_spend.get(cat, 0.0) + txn.amount
        category_rewards[cat] = category_rewards.get(cat, 0.0) + (txn.reward_points or 0.0)

    total_spend = sum(category_spend.values())
    total_rewards = sum(category_rewards.values())

    # Highest absolute reward category
    highest_reward_category = max(category_rewards, key=category_rewards.get) if category_rewards else None

    # Highest reward rate category (rewards per rupee spent)
    reward_rates = {}
    for cat in category_spend:
        if category_spend[cat] > 0:
            reward_rates[cat] = category_rewards.get(cat, 0.0) / category_spend[cat]

    highest_reward_rate_category = max(reward_rates, key=reward_rates.get) if reward_rates else None

    # Round all values for clean output
    category_spend = {k: round(v, 2) for k, v in category_spend.items()}
    category_rewards = {k: round(v, 2) for k, v in category_rewards.items()}

    return {
        "month": month,
        "total_spend": round(total_spend, 2),
        "total_rewards": round(total_rewards, 2),
        "category_spend": category_spend,
        "category_rewards": category_rewards,
        "highest_reward_category": highest_reward_category,
        "highest_reward_rate_category": highest_reward_rate_category,
        "transaction_count": len(transactions),
    }


def get_multi_month_trends(db: Session, months: List[str], bank: Optional[str] = None) -> dict:
    """
    Compute trends across multiple months.
    months should be sorted chronologically (e.g., ["2026-01", "2026-02", ...]).
    """
    months = sorted(months)

    spend_by_category = {}
    rewards_by_category = {}
    total_spend_trend = []
    total_rewards_trend = []
    highest_reward_category_trend = []

    for month in months:
        analytics = get_monthly_analytics(db, month, bank)
        total_spend_trend.append(analytics["total_spend"])
        total_rewards_trend.append(analytics["total_rewards"])
        highest_reward_category_trend.append(analytics["highest_reward_category"])

        for cat, amount in analytics["category_spend"].items():
            if cat not in spend_by_category:
                spend_by_category[cat] = []
            spend_by_category[cat].append({"month": month, "amount": amount})

        for cat, points in analytics["category_rewards"].items():
            if cat not in rewards_by_category:
                rewards_by_category[cat] = []
            rewards_by_category[cat].append({"month": month, "points": points})

    # Month-over-month changes
    mom_spend_change = [None]
    for i in range(1, len(total_spend_trend)):
        prev = total_spend_trend[i - 1]
        curr = total_spend_trend[i]
        if prev > 0:
            change = round(((curr - prev) / prev) * 100, 2)
        else:
            change = None
        mom_spend_change.append(change)

    mom_rewards_change = [None]
    for i in range(1, len(total_rewards_trend)):
        prev = total_rewards_trend[i - 1]
        curr = total_rewards_trend[i]
        if prev > 0:
            change = round(((curr - prev) / prev) * 100, 2)
        else:
            change = None
        mom_rewards_change.append(change)

    return {
        "months": months,
        "spend_by_category": spend_by_category,
        "rewards_by_category": rewards_by_category,
        "total_spend_trend": total_spend_trend,
        "total_rewards_trend": total_rewards_trend,
        "mom_spend_change": mom_spend_change,
        "mom_rewards_change": mom_rewards_change,
        "highest_reward_category_trend": highest_reward_category_trend,
    }


def get_available_months(db: Session) -> List[str]:
    """Get list of all months that have statement data."""
    months = db.query(Statement.statement_month).distinct().order_by(Statement.statement_month).all()
    return [m[0] for m in months]


def get_transactions(
    db: Session,
    month: Optional[str] = None,
    category: Optional[str] = None,
    bank: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """Get filtered transactions with pagination."""
    query = db.query(Transaction).join(Statement)

    if month:
        query = query.filter(Statement.statement_month == month)
    if category:
        query = query.filter(func.lower(Transaction.category) == category.lower())
    if bank:
        query = query.filter(Statement.bank.ilike(f"%{bank}%"))

    total = query.count()
    transactions = query.order_by(Transaction.transaction_date.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "transactions": transactions,
    }
