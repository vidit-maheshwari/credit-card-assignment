from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class UserConfig(Base):
    __tablename__ = "user_config"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Statement(Base):
    __tablename__ = "statements"

    id = Column(Integer, primary_key=True, index=True)
    bank = Column(String, nullable=False)
    card_type = Column(String, nullable=True)
    statement_month = Column(String, nullable=False)  # Format: YYYY-MM
    filename = Column(String, nullable=False)
    file_hash = Column(String, nullable=False, unique=True)
    imported_at = Column(DateTime, server_default=func.now())

    transactions = relationship("Transaction", back_populates="statement", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    statement_id = Column(Integer, ForeignKey("statements.id"), nullable=False)
    transaction_date = Column(Date, nullable=False)
    merchant_description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # "debit" or "credit"
    reward_points = Column(Float, nullable=True, default=0.0)
    category = Column(String, nullable=False, default="Other")
    raw_category = Column(String, nullable=True)

    statement = relationship("Statement", back_populates="transactions")
