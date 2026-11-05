import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False, default="checking")  # checking, savings, cash, credit_card, investment, loan
    initial_balance = Column(Float, default=0.0)
    current_balance = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    icon = Column(String(50), default="wallet")
    color = Column(String(30), default="#3b82f6")
    is_liability = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    transactions = relationship("Transaction", back_populates="account", foreign_keys="Transaction.account_id", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # income, expense
    icon = Column(String(50), default="tag")
    color = Column(String(30), default="#10b981")

    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    to_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    type = Column(String(20), nullable=False)  # income, expense, transfer
    amount = Column(Float, nullable=False)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD
    payee = Column(String(150), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    account = relationship("Account", foreign_keys=[account_id], back_populates="transactions")
    to_account = relationship("Account", foreign_keys=[to_account_id])
    category = relationship("Category", back_populates="transactions")

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    amount = Column(Float, nullable=False)
    period = Column(String(20), default="monthly")  # e.g., 'monthly' or '2026-11'

    category = relationship("Category", back_populates="budgets")

class DebtGoal(Base):
    __tablename__ = "debt_goals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    type = Column(String(30), nullable=False)  # 'i_owe' (liability), 'they_owe_me' (receivable)
    counterparty = Column(String(150), nullable=True)
    total_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0.0)
    due_date = Column(String(10), nullable=True)
    interest_rate = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    status = Column(String(20), default="active")  # active, completed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
