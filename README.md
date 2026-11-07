# WealthPulse — Personal Accounting & Wealth OS

A modern, full-stack personal accounting and wealth management system built with **FastAPI**, **SQLite**, and **React + Vite + Tailwind CSS**.

---

## 🌟 Key Features

1. **Dashboard & Financial Health Summary**:
   - Real-time **Net Worth** tracking (Total Assets minus Total Liabilities).
   - Monthly cash flow metrics: Total Income, Total Expenses, Net Savings, and Savings Rate (%).
   - Interactive 6-month & 12-month Income vs. Expense bar and area charts.
   - Donut charts for category expense distribution.

2. **Multi-Account & Wallet Management**:
   - Manage checking, savings (HYSA), physical cash, investment/brokerage accounts, and credit card / loan liabilities.
   - Automatic balance reconciliation based on income, expenses, and inter-account transfers.
   - Custom accent colors and account classifications.

3. **Transaction Ledger & Tracking**:
   - Track Income, Expenses, and Account Transfers with date, payee, category, and notes.
   - Fast filtering by account, category, type, and live search.
   - **CSV Export & Import**: Seamlessly export records or upload bank statement CSV files.

4. **Monthly Category Budgets**:
   - Set monthly budget limits per expense category.
   - Visual progress bars with color-coded warning states (On Track, Near Limit, Over Budget).
   - Real-time remaining budget calculations.

5. **Debts & Receivables Tracker**:
   - Track liabilities (money you owe to lenders or credit) and receivables (money others owe to you).
   - Interest rate tracking (APR) and due dates.
   - "Record Payment" dialog to track paydowns until 100% completed.

6. **Financial Reports & Analytics**:
   - Historical multi-month cash flow analysis.
   - Ranked category expenditure tables.
   - 30-day daily cashflow velocity.

---

## 🚀 Quick Start

### One-Click Launch (Windows)
Double-click `run.bat` or run:
```powershell
.\run.bat
```
*(Or in PowerShell: `.\run.ps1`)*

This starts both the FastAPI backend (`http://127.0.0.1:8000`) and the Vite React frontend (`http://localhost:5173`) and opens the browser automatically.

---

## 🛠 Manual Execution

### 1. Backend Setup
```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Run FastAPI server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive API documentation will be available at: **http://127.0.0.1:8000/docs**

### 2. Frontend Setup
```bash
cd frontend
npm run dev
```
Open your browser at: **http://localhost:5173**

---

## 📁 Project Architecture

```
personal accounting soft/
├── backend/
│   ├── database.py       # SQLite connection & session maker
│   ├── models.py         # SQLAlchemy ORM models (Account, Transaction, Category, Budget, DebtGoal)
│   ├── schemas.py        # Pydantic v2 validation models
│   ├── crud.py           # Database queries, balance auto-recalculation, filters
│   ├── analytics.py      # Net worth, monthly trends, cashflow aggregations
│   ├── seed_data.py      # Seed demo categories, accounts, and sample ledger data
│   └── main.py           # FastAPI REST endpoints, CORS, CSV export/import
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx           # Navigation bar with quick stats and action buttons
│   │   │   ├── Overview.tsx         # Dashboard KPI cards and Recharts visualizations
│   │   │   ├── AccountsView.tsx     # Account wallets and liability manager
│   │   │   ├── TransactionsView.tsx # Ledger table, filters, search, CSV import/export
│   │   │   ├── BudgetsView.tsx      # Monthly spending goals and progress bars
│   │   │   ├── DebtsView.tsx        # Debt & receivable payoff tracker
│   │   │   ├── AnalyticsView.tsx    # Multi-month reports and area trend charts
│   │   │   └── TransactionModal.tsx # Universal transaction recording modal
│   │   ├── api.ts                   # Fetch API wrapper
│   │   ├── types.ts                 # TypeScript interfaces
│   │   └── App.tsx                  # Main app container and tab navigation
│   ├── package.json
│   └── vite.config.ts
├── run.bat               # Windows one-click launcher
├── run.ps1               # PowerShell launcher
└── README.md
```

