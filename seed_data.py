from sqlalchemy.orm import Session
import datetime
from . import models, crud

DEFAULT_CATEGORIES = [
    # Expenses matching the ledger
    {"name": "Transportation & Bike Oil", "type": "expense", "icon": "car", "color": "#6366f1"},
    {"name": "Company Registration", "type": "expense", "icon": "briefcase", "color": "#06b6d4"},
    {"name": "Seal & Brochure (Marketing)", "type": "expense", "icon": "file-text", "color": "#8b5cf6"},
    {"name": "Food & Lunch", "type": "expense", "icon": "coffee", "color": "#f59e0b"},
    {"name": "Course & Education", "type": "expense", "icon": "book-open", "color": "#10b981"},
    {"name": "Loan Given (Receivable)", "type": "expense", "icon": "scale", "color": "#ec4899"},
    {"name": "Investments & Capital", "type": "expense", "icon": "trending-up", "color": "#9333ea"},
    {"name": "General Expenses", "type": "expense", "icon": "tag", "color": "#64748b"},
    # Incomes
    {"name": "Salary & Client Revenue", "type": "income", "icon": "dollar-sign", "color": "#10b981"},
    {"name": "Loan Repayment (Taka In)", "type": "income", "icon": "arrow-down-left", "color": "#3b82f6"},
]

def seed_database(db: Session, force: bool = False):
    existing_acc_count = db.query(models.Account).count()
    if existing_acc_count > 0 and not force:
        return

    # Always wipe cleanly when force=True
    db.query(models.Transaction).delete()
    db.query(models.Budget).delete()
    db.query(models.DebtGoal).delete()
    db.query(models.Account).delete()
    db.query(models.Category).delete()
    db.commit()

    # 1. Insert Categories
    cat_map = {}
    for c in DEFAULT_CATEGORIES:
        category = models.Category(**c)
        db.add(category)
        db.commit()
        db.refresh(category)
        cat_map[category.name] = category.id

    # 2. Insert Accounts with 0 initial balance as requested
    cash_wallet = models.Account(
        name="Cash Wallet",
        type="cash",
        initial_balance=0.0,
        current_balance=0.0,
        currency="BDT",
        icon="banknote",
        color="#f59e0b",
        is_liability=False,
        notes="Primary cash account"
    )
    bank_acc = models.Account(
        name="Main Bank Account",
        type="checking",
        initial_balance=0.0,
        current_balance=0.0,
        currency="BDT",
        icon="landmark",
        color="#2563eb",
        is_liability=False,
        notes="Bank account for online & card transactions"
    )
    mobile_wallet = models.Account(
        name="bKash",
        type="cash",
        initial_balance=0.0,
        current_balance=0.0,
        currency="BDT",
        icon="wallet",
        color="#ec4899",
        is_liability=False,
        notes="bKash mobile financial service account"
    )
    nagad_wallet = models.Account(
        name="Nagad",
        type="cash",
        initial_balance=0.0,
        current_balance=0.0,
        currency="BDT",
        icon="wallet",
        color="#ea580c",
        is_liability=False,
        notes="Nagad mobile financial service account"
    )

    db.add_all([cash_wallet, bank_acc, mobile_wallet, nagad_wallet])
    db.commit()
    for acc in [cash_wallet, bank_acc, mobile_wallet, nagad_wallet]:
        db.refresh(acc)

    # 3. Add the 13 records from the user's sheet (Total: 12,840 BDT)
    raw_records = [
        # Pulsecode records
        {
            "tag": "Pulsecode",
            "date": "2026-09-15",
            "details": "Give loan",
            "comments": "Loan given to Pulsecode",
            "amount": 1500.0,
            "category": "Loan Given (Receivable)"
        },
        {
            "tag": "Pulsecode",
            "date": "2026-09-17",
            "details": "Bike oil",
            "comments": "SHQ",
            "amount": 150.0,
            "category": "Transportation & Bike Oil"
        },
        {
            "tag": "Pulsecode",
            "date": "2026-09-18",
            "details": "Lunch",
            "comments": "Total bill 480 / Taka out 380",
            "amount": 380.0,
            "category": "Food & Lunch"
        },
        {
            "tag": "Pulsecode",
            "date": "2026-09-20",
            "details": "Sil + brocheare",
            "comments": "Seal and brochure printing",
            "amount": 1500.0,
            "category": "Seal & Brochure (Marketing)"
        },
        {
            "tag": "Pulsecode",
            "date": "2026-09-22",
            "details": "Company reg",
            "comments": "sole proprietorship",
            "amount": 5000.0,
            "category": "Company Registration"
        },
        {
            "tag": "Pulsecode",
            "date": "2026-09-25",
            "details": "sil",
            "comments": "bike oil",
            "amount": 150.0,
            "category": "Transportation & Bike Oil"
        },
        {
            "tag": "Pulsecode",
            "date": "2026-09-30",
            "details": "bike oil",
            "comments": "29-30 trik",
            "amount": 150.0,
            "category": "Transportation & Bike Oil"
        },
        {
            "tag": "Pulsecode",
            "date": "2026-10-05",
            "details": "bike oil",
            "comments": "SHQ",
            "amount": 170.0,
            "category": "Transportation & Bike Oil"
        },
        {
            "tag": "Pulsecode",
            "date": "2026-10-12",
            "details": "bike oil",
            "comments": "SHQ",
            "amount": 170.0,
            "category": "Transportation & Bike Oil"
        },
        {
            "tag": "Pulsecode",
            "date": "2026-10-19",
            "details": "bike oil",
            "comments": "SHQ",
            "amount": 170.0,
            "category": "Transportation & Bike Oil"
        },
        {
            "tag": "Pulsecode",
            "date": "2026-11-05",
            "details": "for Course",
            "comments": "2000 TK course payment",
            "amount": 1000.0,
            "category": "Course & Education"
        },
        # Rifat records
        {
            "tag": "Rifat",
            "date": "2026-10-20",
            "details": "Taka out (Loan)",
            "comments": "Loan to Rifat",
            "amount": 2000.0,
            "category": "Loan Given (Receivable)"
        },
        {
            "tag": "Rifat",
            "date": "2026-10-26",
            "details": "Taka out (Loan)",
            "comments": "Additional payment to Rifat",
            "amount": 500.0,
            "category": "Loan Given (Receivable)"
        },
    ]

    for item in raw_records:
        payee_label = f"[{item['tag']}] {item['details']}"
        tx = models.Transaction(
            account_id=cash_wallet.id,
            category_id=cat_map[item['category']],
            type="expense",
            amount=item['amount'],
            date=item['date'],
            payee=payee_label,
            notes=item['comments']
        )
        db.add(tx)
    db.commit()

    # Recalculate account balances
    crud.update_account_balance(db, cash_wallet.id)

    # 4. Insert Debt & Receivable Goals for Pulsecode & Rifat
    debts = [
        models.DebtGoal(
            title="Loan to Pulsecode",
            type="they_owe_me",
            counterparty="Pulsecode",
            total_amount=1500.0,
            paid_amount=0.0,
            due_date="2026-12-31",
            interest_rate=0.0,
            notes="Give loan (Initial 1500 TK)",
            status="active"
        ),
        models.DebtGoal(
            title="Loan to Rifat",
            type="they_owe_me",
            counterparty="Rifat",
            total_amount=2500.0,  # 2000 + 500
            paid_amount=0.0,
            due_date="2026-12-31",
            interest_rate=0.0,
            notes="Taka out (2000 + 500 TK on 26/10/26)",
            status="active"
        ),
    ]
    db.add_all(debts)
    db.commit()
