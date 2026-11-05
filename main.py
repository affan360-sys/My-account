import csv
import io
import datetime
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from .database import engine, Base, get_db
from . import models, schemas, crud, analytics
from .seed_data import seed_database

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Affan Accounting Engine",
    description="Full-featured personal wealth & accounting backend",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    db = next(get_db())
    try:
        seed_database(db, force=False)
    finally:
        db.close()

# --- Health check ---
@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "WealthPulse API"}

# --- Summary & Analytics ---
@app.get("/api/summary", response_model=schemas.FinancialSummary)
def get_summary(db: Session = Depends(get_db)):
    return analytics.get_financial_summary(db)

@app.get("/api/analytics/monthly", response_model=List[schemas.MonthlyTrend])
def get_monthly_trends(months: int = Query(6, ge=1, le=24), db: Session = Depends(get_db)):
    return analytics.get_monthly_trends(db, months_count=months)

@app.get("/api/analytics/category-breakdown", response_model=List[schemas.CategoryBreakdown])
def get_category_breakdown(month: Optional[str] = None, db: Session = Depends(get_db)):
    return analytics.get_category_breakdown(db, month=month)

@app.get("/api/analytics/cashflow")
def get_cashflow(days: int = Query(30, ge=7, le=90), db: Session = Depends(get_db)):
    return analytics.get_recent_cashflow(db, days=days)

# --- Accounts ---
@app.get("/api/accounts", response_model=List[schemas.Account])
def list_accounts(db: Session = Depends(get_db)):
    return crud.get_accounts(db)

@app.post("/api/accounts", response_model=schemas.Account)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    return crud.create_account(db, account)

@app.put("/api/accounts/{account_id}", response_model=schemas.Account)
def update_account(account_id: int, account: schemas.AccountUpdate, db: Session = Depends(get_db)):
    res = crud.update_account(db, account_id, account)
    if not res:
        raise HTTPException(status_code=404, detail="Account not found")
    return res

@app.delete("/api/accounts/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    if not crud.delete_account(db, account_id):
        raise HTTPException(status_code=404, detail="Account not found")
    return {"ok": True}

# --- Categories ---
@app.get("/api/categories", response_model=List[schemas.Category])
def list_categories(type: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_categories(db, cat_type=type)

@app.post("/api/categories", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db, category)

@app.delete("/api/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    if not crud.delete_category(db, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"ok": True}

# --- Transactions ---
@app.get("/api/transactions")
def list_transactions(
    account_id: Optional[int] = None,
    category_id: Optional[int] = None,
    type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    items, total = crud.get_transactions(
        db,
        account_id=account_id,
        category_id=category_id,
        trans_type=type,
        start_date=start_date,
        end_date=end_date,
        search=search,
        limit=limit,
        offset=offset
    )
    return {"items": items, "total": total}

@app.post("/api/transactions", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db, transaction)

@app.put("/api/transactions/{transaction_id}", response_model=schemas.Transaction)
def update_transaction(transaction_id: int, transaction: schemas.TransactionUpdate, db: Session = Depends(get_db)):
    t = crud.update_transaction(db, transaction_id, transaction)
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return t

@app.delete("/api/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    if not crud.delete_transaction(db, transaction_id):
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"ok": True}

# --- Budgets ---
@app.get("/api/budgets", response_model=List[schemas.Budget])
def list_budgets(month: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_budgets(db, month_prefix=month)

@app.post("/api/budgets", response_model=schemas.Budget)
def set_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db)):
    return crud.create_or_update_budget(db, budget)

@app.delete("/api/budgets/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    if not crud.delete_budget(db, budget_id):
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"ok": True}

# --- Debts / Loans ---
@app.get("/api/debts", response_model=List[schemas.DebtGoal])
def list_debts(db: Session = Depends(get_db)):
    return crud.get_debts(db)

@app.post("/api/debts", response_model=schemas.DebtGoal)
def create_debt(debt: schemas.DebtGoalCreate, db: Session = Depends(get_db)):
    return crud.create_debt(db, debt)

@app.put("/api/debts/{debt_id}", response_model=schemas.DebtGoal)
def update_debt(debt_id: int, debt: schemas.DebtGoalUpdate, db: Session = Depends(get_db)):
    res = crud.update_debt(db, debt_id, debt)
    if not res:
        raise HTTPException(status_code=404, detail="Debt not found")
    return res

@app.delete("/api/debts/{debt_id}")
def delete_debt(debt_id: int, db: Session = Depends(get_db)):
    if not crud.delete_debt(db, debt_id):
        raise HTTPException(status_code=404, detail="Debt not found")
    return {"ok": True}

# --- CSV Import & Export ---
@app.get("/api/export/csv")
def export_csv(db: Session = Depends(get_db)):
    items, _ = crud.get_transactions(db, limit=10000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Date", "Type", "Amount", "Payee", "Category", "Account", "To Account", "Notes"])
    for t in items:
        writer.writerow([
            t["id"],
            t["date"],
            t["type"],
            t["amount"],
            t["payee"] or "",
            t["category_name"] or "",
            t["account_name"] or "",
            t["to_account_name"] or "",
            t["notes"] or ""
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions_export.csv"}
    )

@app.post("/api/import/csv")
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    decoded = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))
    
    # Get or default accounts and categories
    accounts = {a.name.lower(): a.id for a in crud.get_accounts(db)}
    categories = {c.name.lower(): c.id for c in crud.get_categories(db)}
    default_acc_id = next(iter(accounts.values())) if accounts else None
    
    if not default_acc_id:
        raise HTTPException(status_code=400, detail="Please create at least one account before importing.")

    count = 0
    for row in reader:
        date = row.get("Date") or row.get("date")
        amount_str = row.get("Amount") or row.get("amount") or "0"
        try:
            amount = abs(float(amount_str.replace("$", "").replace(",", "").strip()))
        except ValueError:
            continue
        
        t_type = (row.get("Type") or row.get("type") or "expense").strip().lower()
        if t_type not in ["income", "expense", "transfer"]:
            t_type = "expense"

        payee = row.get("Payee") or row.get("payee") or row.get("Description") or row.get("description") or "Unknown"
        cat_str = (row.get("Category") or row.get("category") or "").strip().lower()
        cat_id = categories.get(cat_str)
        
        acc_str = (row.get("Account") or row.get("account") or "").strip().lower()
        acc_id = accounts.get(acc_str, default_acc_id)

        t_obj = schemas.TransactionCreate(
            account_id=acc_id,
            category_id=cat_id,
            type=t_type,
            amount=amount,
            date=date or str(datetime.date.today()),
            payee=payee,
            notes=row.get("Notes") or row.get("notes") or ""
        )
        crud.create_transaction(db, t_obj)
        count += 1

    return {"imported": count}

# --- Seed Reset ---
@app.post("/api/seed/reset")
def reset_seed(db: Session = Depends(get_db)):
    seed_database(db, force=True)
    return {"message": "Database reset to sample demo data"}

# --- Native Notification Test ---
@app.post("/api/notifications/test")
def test_native_notification():
    from .send_toast import send_windows_toast
    success = send_windows_toast()
    return {"status": "ok", "sent": success}

