from pydantic import BaseModel, Field
from typing import Optional, List
import datetime

# --- Categories ---
class CategoryBase(BaseModel):
    name: str
    type: str  # 'income' or 'expense'
    icon: Optional[str] = "tag"
    color: Optional[str] = "#10b981"

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True


# --- Accounts ---
class AccountBase(BaseModel):
    name: str
    type: str = "checking"  # checking, savings, cash, credit_card, investment, loan
    initial_balance: float = 0.0
    currency: str = "USD"
    icon: Optional[str] = "wallet"
    color: Optional[str] = "#3b82f6"
    is_liability: bool = False
    notes: Optional[str] = None

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    currency: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_liability: Optional[bool] = None
    notes: Optional[str] = None

class Account(AccountBase):
    id: int
    current_balance: float
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- Transactions ---
class TransactionBase(BaseModel):
    account_id: int
    category_id: Optional[int] = None
    to_account_id: Optional[int] = None
    type: str  # 'income', 'expense', 'transfer'
    amount: float
    date: str  # YYYY-MM-DD
    payee: Optional[str] = None
    notes: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    account_id: Optional[int] = None
    category_id: Optional[int] = None
    to_account_id: Optional[int] = None
    type: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[str] = None
    payee: Optional[str] = None
    notes: Optional[str] = None

class Transaction(TransactionBase):
    id: int
    created_at: datetime.datetime
    account_name: Optional[str] = None
    category_name: Optional[str] = None
    to_account_name: Optional[str] = None

    class Config:
        from_attributes = True


# --- Budgets ---
class BudgetBase(BaseModel):
    category_id: int
    amount: float
    period: str = "monthly"

class BudgetCreate(BudgetBase):
    pass

class Budget(BudgetBase):
    id: int
    category: Optional[Category] = None
    spent: float = 0.0
    remaining: float = 0.0
    percentage: float = 0.0

    class Config:
        from_attributes = True


# --- Debt / Goals ---
class DebtGoalBase(BaseModel):
    title: str
    type: str  # 'i_owe', 'they_owe_me'
    counterparty: Optional[str] = None
    total_amount: float
    paid_amount: float = 0.0
    due_date: Optional[str] = None
    interest_rate: float = 0.0
    notes: Optional[str] = None
    status: str = "active"

class DebtGoalCreate(DebtGoalBase):
    pass

class DebtGoalUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    counterparty: Optional[str] = None
    total_amount: Optional[float] = None
    paid_amount: Optional[float] = None
    due_date: Optional[str] = None
    interest_rate: Optional[float] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class DebtGoal(DebtGoalBase):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- Analytics & Summaries ---
class FinancialSummary(BaseModel):
    net_worth: float
    total_assets: float
    total_liabilities: float
    total_receivable: float = 0.0
    total_payable: float = 0.0
    total_income_this_month: float
    total_expense_this_month: float
    net_savings_this_month: float
    savings_rate_pct: float

class MonthlyTrend(BaseModel):
    month: str  # e.g. "2026-06", "Jun"
    income: float
    expense: float
    net: float

class CategoryBreakdown(BaseModel):
    category_name: str
    category_color: str
    amount: float
    percentage: float

class NetWorthTrend(BaseModel):
    month: str
    net_worth: float
    assets: float
    liabilities: float

