from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class TransactionOut(BaseModel):
    id: int
    statement_id: int
    transaction_date: date
    merchant_description: str
    amount: float
    transaction_type: str
    reward_points: Optional[float] = 0.0
    category: str
    raw_category: Optional[str] = None

    class Config:
        from_attributes = True


class StatementOut(BaseModel):
    id: int
    bank: str
    card_type: Optional[str] = None
    statement_month: str
    filename: str
    imported_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MonthlyAnalytics(BaseModel):
    month: str
    total_spend: float
    total_rewards: float
    category_spend: dict
    category_rewards: dict
    highest_reward_category: Optional[str] = None
    highest_reward_rate_category: Optional[str] = None


class TrendData(BaseModel):
    months: List[str]
    spend_by_category: dict
    rewards_by_category: dict
    total_spend_trend: List[float]
    total_rewards_trend: List[float]
    mom_spend_change: List[Optional[float]]
    mom_rewards_change: List[Optional[float]]
    highest_reward_category_trend: List[Optional[str]]


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    data: Optional[dict] = None


class IngestResponse(BaseModel):
    ingested: int
    skipped: int
    errors: List[str]
