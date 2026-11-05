from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional
import datetime
from . import models, schemas

def get_financial_summary(db: Session) -> Dict[str, Any]:
    # 1. Accounts assets vs liabilities
    accounts = db.query(models.Account).all()
    total_assets = sum(a.current_balance for a in accounts if not a.is_liability)
    total_liabilities = sum(a.current_balance for a in accounts if a.is_liability)
    net_worth = total_assets - total_liabilities

    # 2. Receivables & Payables
    debts = db.query(models.DebtGoal).filter(models.DebtGoal.status == "active").all()
    total_receivable = sum(max(0.0, d.total_amount - d.paid_amount) for d in debts if d.type == "they_owe_me")
    total_payable = sum(max(0.0, d.total_amount - d.paid_amount) for d in debts if d.type == "i_owe")

    # 3. Current Month Income & Expense
    current_month = datetime.date.today().strftime("%Y-%m")
    
    total_income = db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0)).filter(
        models.Transaction.type == "income",
        models.Transaction.date.like(f"{current_month}%")
    ).scalar() or 0.0

    total_expense = db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0)).filter(
        models.Transaction.type == "expense",
        models.Transaction.date.like(f"{current_month}%")
    ).scalar() or 0.0

    net_savings = total_income - total_expense
    savings_rate_pct = (net_savings / total_income * 100.0) if total_income > 0 else 0.0

    return {
        "net_worth": round(net_worth, 2),
        "total_assets": round(total_assets, 2),
        "total_liabilities": round(total_liabilities, 2),
        "total_receivable": round(total_receivable, 2),
        "total_payable": round(total_payable, 2),
        "total_income_this_month": round(total_income, 2),
        "total_expense_this_month": round(total_expense, 2),
        "net_savings_this_month": round(net_savings, 2),
        "savings_rate_pct": round(savings_rate_pct, 1)
    }

def get_monthly_trends(db: Session, months_count: int = 6) -> List[Dict[str, Any]]:
    # Generate list of past N months (YYYY-MM)
    today = datetime.date.today()
    months = []
    for i in range(months_count - 1, -1, -1):
        # Approximate month offset
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
        months.append(f"{year:04d}-{month:02d}")

    trend_data = []
    for m in months:
        inc = db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0)).filter(
            models.Transaction.type == "income",
            models.Transaction.date.like(f"{m}%")
        ).scalar() or 0.0

        exp = db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0)).filter(
            models.Transaction.type == "expense",
            models.Transaction.date.like(f"{m}%")
        ).scalar() or 0.0

        # Parse pretty label, e.g. "Jun 2026"
        dt = datetime.datetime.strptime(m, "%Y-%m")
        pretty_label = dt.strftime("%b %y")

        trend_data.append({
            "month": pretty_label,
            "raw_month": m,
            "income": round(inc, 2),
            "expense": round(exp, 2),
            "net": round(inc - exp, 2)
        })

    return trend_data

def get_category_breakdown(db: Session, month: Optional[str] = None) -> List[Dict[str, Any]]:
    if not month:
        month = datetime.date.today().strftime("%Y-%m")

    # Group expenses by category
    results = db.query(
        models.Category.name,
        models.Category.color,
        func.coalesce(func.sum(models.Transaction.amount), 0.0).label("total")
    ).join(models.Transaction, models.Transaction.category_id == models.Category.id).filter(
        models.Transaction.type == "expense",
        models.Transaction.date.like(f"{month}%")
    ).group_by(models.Category.id).order_by(func.sum(models.Transaction.amount).desc()).all()

    total_spent = sum(r[2] for r in results) or 1.0

    breakdown = []
    for cat_name, color, amount in results:
        breakdown.append({
            "category_name": cat_name,
            "category_color": color or "#3b82f6",
            "amount": round(amount, 2),
            "percentage": round((amount / total_spent) * 100.0, 1)
        })

    return breakdown

def get_recent_cashflow(db: Session, days: int = 30) -> List[Dict[str, Any]]:
    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=days)).strftime("%Y-%m-%d")

    records = db.query(
        models.Transaction.date,
        models.Transaction.type,
        func.sum(models.Transaction.amount).label("amount")
    ).filter(
        models.Transaction.date >= start_date,
        models.Transaction.type.in_(["income", "expense"])
    ).group_by(models.Transaction.date, models.Transaction.type).all()

    # Aggregate by date
    daily_map = {}
    for d, t_type, amt in records:
        if d not in daily_map:
            daily_map[d] = {"date": d, "income": 0.0, "expense": 0.0}
        if t_type == "income":
            daily_map[d]["income"] += amt
        else:
            daily_map[d]["expense"] += amt

    sorted_days = sorted(daily_map.values(), key=lambda x: x["date"])
    return sorted_days

