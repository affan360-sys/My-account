from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional, List
import datetime
from . import models, schemas

def update_account_balance(db: Session, account_id: int):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        return
    
    # Calculate all incoming
    # 1. Income transactions to this account
    income_sum = db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0)).filter(
        models.Transaction.account_id == account_id,
        models.Transaction.type == "income"
    ).scalar() or 0.0

    # 2. Transfers into this account
    transfers_in = db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0)).filter(
        models.Transaction.to_account_id == account_id,
        models.Transaction.type == "transfer"
    ).scalar() or 0.0

    # Calculate all outgoing
    # 3. Expense transactions from this account
    expense_sum = db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0)).filter(
        models.Transaction.account_id == account_id,
        models.Transaction.type == "expense"
    ).scalar() or 0.0

    # 4. Transfers out from this account
    transfers_out = db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0)).filter(
        models.Transaction.account_id == account_id,
        models.Transaction.type == "transfer"
    ).scalar() or 0.0

    if account.is_liability:
        # For credit cards / loans, higher expense means higher balance owed (liability)
        account.current_balance = account.initial_balance + expense_sum + transfers_out - income_sum - transfers_in
    else:
        # Standard asset: initial + income + transfers_in - expense - transfers_out
        account.current_balance = account.initial_balance + income_sum + transfers_in - expense_sum - transfers_out
    
    db.commit()
    db.refresh(account)

# --- Accounts ---
def get_accounts(db: Session):
    return db.query(models.Account).all()

def get_account(db: Session, account_id: int):
    return db.query(models.Account).filter(models.Account.id == account_id).first()

def create_account(db: Session, account_in: schemas.AccountCreate):
    account = models.Account(
        name=account_in.name,
        type=account_in.type,
        initial_balance=account_in.initial_balance,
        current_balance=account_in.initial_balance,
        currency=account_in.currency,
        icon=account_in.icon or "wallet",
        color=account_in.color or "#3b82f6",
        is_liability=account_in.is_liability or account_in.type in ["credit_card", "loan"],
        notes=account_in.notes
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

def update_account(db: Session, account_id: int, account_in: schemas.AccountUpdate):
    account = get_account(db, account_id)
    if not account:
        return None
    for field, value in account_in.dict(exclude_unset=True).items():
        setattr(account, field, value)
    db.commit()
    db.refresh(account)
    update_account_balance(db, account_id)
    return account

def delete_account(db: Session, account_id: int):
    account = get_account(db, account_id)
    if account:
        db.delete(account)
        db.commit()
        return True
    return False

# --- Categories ---
def get_categories(db: Session, cat_type: Optional[str] = None):
    query = db.query(models.Category)
    if cat_type:
        query = query.filter(models.Category.type == cat_type)
    return query.all()

def create_category(db: Session, cat_in: schemas.CategoryCreate):
    category = models.Category(
        name=cat_in.name,
        type=cat_in.type,
        icon=cat_in.icon or "tag",
        color=cat_in.color or "#10b981"
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def delete_category(db: Session, category_id: int):
    cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if cat:
        db.delete(cat)
        db.commit()
        return True
    return False

# --- Transactions ---
def get_transactions(
    db: Session,
    account_id: Optional[int] = None,
    category_id: Optional[int] = None,
    trans_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    query = db.query(models.Transaction)
    if account_id:
        query = query.filter((models.Transaction.account_id == account_id) | (models.Transaction.to_account_id == account_id))
    if category_id:
        query = query.filter(models.Transaction.category_id == category_id)
    if trans_type:
        query = query.filter(models.Transaction.type == trans_type)
    if start_date:
        query = query.filter(models.Transaction.date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.date <= end_date)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (models.Transaction.payee.ilike(search_pattern)) | 
            (models.Transaction.notes.ilike(search_pattern))
        )
    
    total = query.count()
    items = query.order_by(models.Transaction.date.desc(), models.Transaction.id.desc()).offset(offset).limit(limit).all()

    # Enrich with names
    result = []
    for t in items:
        trans_dict = {
            "id": t.id,
            "account_id": t.account_id,
            "category_id": t.category_id,
            "to_account_id": t.to_account_id,
            "type": t.type,
            "amount": t.amount,
            "date": t.date,
            "payee": t.payee,
            "notes": t.notes,
            "created_at": t.created_at,
            "account_name": t.account.name if t.account else None,
            "category_name": t.category.name if t.category else ("Transfer" if t.type == "transfer" else None),
            "to_account_name": t.to_account.name if t.to_account else None
        }
        result.append(trans_dict)
    return result, total

def create_transaction(db: Session, t_in: schemas.TransactionCreate):
    transaction = models.Transaction(
        account_id=t_in.account_id,
        category_id=t_in.category_id,
        to_account_id=t_in.to_account_id,
        type=t_in.type,
        amount=t_in.amount,
        date=t_in.date,
        payee=t_in.payee,
        notes=t_in.notes
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # Update account balances
    update_account_balance(db, t_in.account_id)
    if t_in.to_account_id:
        update_account_balance(db, t_in.to_account_id)

    return transaction

def update_transaction(db: Session, transaction_id: int, t_in: schemas.TransactionUpdate):
    t = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not t:
        return None
    
    old_account_id = t.account_id
    old_to_account_id = t.to_account_id

    for field, val in t_in.dict(exclude_unset=True).items():
        setattr(t, field, val)
    db.commit()
    db.refresh(t)

    # Recalculate
    update_account_balance(db, old_account_id)
    if old_to_account_id:
        update_account_balance(db, old_to_account_id)
    if t.account_id != old_account_id:
        update_account_balance(db, t.account_id)
    if t.to_account_id and t.to_account_id != old_to_account_id:
        update_account_balance(db, t.to_account_id)

    return t

def delete_transaction(db: Session, transaction_id: int):
    t = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not t:
        return False
    account_id = t.account_id
    to_account_id = t.to_account_id
    db.delete(t)
    db.commit()

    update_account_balance(db, account_id)
    if to_account_id:
        update_account_balance(db, to_account_id)
    return True

# --- Budgets ---
def get_budgets(db: Session, month_prefix: Optional[str] = None):
    # e.g. month_prefix = "2026-11"
    budgets = db.query(models.Budget).all()
    if not month_prefix:
        month_prefix = datetime.date.today().strftime("%Y-%m")

    res = []
    for b in budgets:
        # Sum expenses in this category for this month
        spent = db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0)).filter(
            models.Transaction.category_id == b.category_id,
            models.Transaction.type == "expense",
            models.Transaction.date.like(f"{month_prefix}%")
        ).scalar() or 0.0

        remaining = b.amount - spent
        pct = (spent / b.amount * 100.0) if b.amount > 0 else 0.0

        res.append({
            "id": b.id,
            "category_id": b.category_id,
            "category": b.category,
            "amount": b.amount,
            "period": b.period,
            "spent": round(spent, 2),
            "remaining": round(remaining, 2),
            "percentage": round(pct, 1)
        })
    return res

def create_or_update_budget(db: Session, b_in: schemas.BudgetCreate):
    existing = db.query(models.Budget).filter(models.Budget.category_id == b_in.category_id).first()
    if existing:
        existing.amount = b_in.amount
        existing.period = b_in.period
        db.commit()
        db.refresh(existing)
        return existing
    budget = models.Budget(category_id=b_in.category_id, amount=b_in.amount, period=b_in.period)
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget

def delete_budget(db: Session, budget_id: int):
    b = db.query(models.Budget).filter(models.Budget.id == budget_id).first()
    if b:
        db.delete(b)
        db.commit()
        return True
    return False

# --- Debts & Goals ---
def get_debts(db: Session):
    return db.query(models.DebtGoal).all()

def create_debt(db: Session, d_in: schemas.DebtGoalCreate):
    debt = models.DebtGoal(**d_in.dict())
    db.add(debt)
    db.commit()
    db.refresh(debt)
    return debt

def update_debt(db: Session, debt_id: int, d_in: schemas.DebtGoalUpdate):
    debt = db.query(models.DebtGoal).filter(models.DebtGoal.id == debt_id).first()
    if not debt:
        return None
    for field, val in d_in.dict(exclude_unset=True).items():
        setattr(debt, field, val)
    if debt.paid_amount >= debt.total_amount:
        debt.status = "completed"
    db.commit()
    db.refresh(debt)
    return debt

def delete_debt(db: Session, debt_id: int):
    debt = db.query(models.DebtGoal).filter(models.DebtGoal.id == debt_id).first()
    if debt:
        db.delete(debt)
        db.commit()
        return True
    return False

