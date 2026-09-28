# MMI AI Analytics — Intelligent ERP Analytics & Reporting

A production-ready enterprise analytics platform designed for **MMI**. Authorized business leaders and operational managers can query ERP datasets in plain English or Arabic using natural language. The system autonomously determines the analytical operation, validates permissions via server-side RBAC, enforces read-only query security via an AST SQL Security Guard, executes analytical aggregation, and returns interactive visualizations with executive summaries.

---

## 🏛️ System Architecture

```
mmi-ai-analytics/
├── apps/
│   ├── web/                    # React 19 + TypeScript + Vite + ECharts + Vanilla CSS Design System
│   │   ├── src/
│   │   │   ├── components/     # Reusable cards, navigation, ECharts wrapper
│   │   │   ├── context/        # AuthContext (RBAC) & LanguageContext (EN/AR RTL)
│   │   │   ├── pages/          # Dashboard, AI Analytics, Reports, Audit Trail
│   │   │   └── types/          # Strict TypeScript interfaces
│   │   └── public/             # PWA Web Manifest & Service Worker
│   └── api/                    # FastAPI + SQLAlchemy 2.0 + Pydantic v2
│       ├── app/
│       │   ├── api/v1/         # Clean REST routers: auth, dashboard, analytics, reports, audit, health
│       │   ├── core/           # Config, database adapter, security, structured logging
│       │   ├── models/         # SQLAlchemy ORM models (Branch, Product, Customer, Sale, Inventory, Audit)
│       │   ├── schemas/        # Pydantic request/response schemas
│       │   ├── services/       # Analytical services, reports builder, multi-format export
│       │   ├── ai/             # AI Provider abstraction (OpenAI / mock fallback engine)
│       │   ├── analytics/      # Semantic layer & deterministic KPI fast-path engine
│       │   └── security/       # AST SQL Security Guard & RBAC branch isolation
│       └── tests/              # 23 comprehensive integration tests
├── database/
│   ├── migrations/             # Alembic migration revisions
│   ├── schema/                 # ANSI SQL / PostgreSQL reference DDL schema
│   └── seed/                   # Deterministic seeder (50,000+ sales records)
├── docs/
│   └── DEPLOYMENT.md           # Step-by-step deployment to Vercel, Render, and Neon
├── .env.example                # Environment variable specification
├── .gitignore
├── docker-compose.yml          # Optional local PostgreSQL composition
└── README.md
```

---

## ⚡ Key Highlights & Architecture Principles

1. **Database-Agnostic Analytics Layer**:
   - Zero-friction local development on pre-seeded SQLite with deterministic data.
   - 100% production-ready for **PostgreSQL** (Neon/Supabase) or **SQL Server** reporting replica by changing only the `DATABASE_URL` connection string without modifying UI or business logic.
2. **Deterministic Seeding (50,000+ Sales Records)**:
   - 4 Branches: Muscat, Salalah, Sohar, Nizwa.
   - 120 Products across 6 enterprise industrial categories.
   - 60 Enterprise and retail customer accounts.
   - 25 Verified suppliers and inventory records.
   - 50,000+ realistic completed sales records spanning 2024 through September 2026.
3. **Multi-Stage Security & SQL Guard**:
   - Rejects DDL/DML statements (`DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`, `TRUNCATE`, `EXEC`).
   - AST table & column whitelisting.
   - Strict server-side branch restriction injection for branch managers.
   - Hard row limits (`LIMIT 500`) to prevent memory exhaustion / DoS.
4. **Fast-Path KPI Mode**:
   - High-frequency business queries execute via pre-validated deterministic templates with zero external AI latency and cost.
   - Graceful fallback for exploratory queries using configured `OPENAI_MODEL` if an API key is provided.
5. **Bidirectional English / Arabic Support**:
   - Instant language switching.
   - Full CSS RTL layout adaptation (`dir="rtl"`, Cairo Arabic typography).
   - Arabic natural language questions resolve to the same semantic dimensions and KPIs.
6. **Multi-Format Verified Exports**:
   - Live report generation for Sales Summary, Branch Performance, Product Performance, and Inventory Valuation.
   - Real binary exports in **Excel (`.xlsx`)**, **PDF (`.pdf`)**, **Word (`.docx`)**, and **CSV**.
7. **Comprehensive Audit Trail**:
   - Every analytical request is recorded with User ID, Role, Execution Time (ms), SQL Query, Result Count, and Success/Rejection status.

---

## 👥 Demo Accounts (Credentials)

| Role | Email | Password | Scope & Permissions |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin@mmi-demo.com` | `Demo@12345` | Global Company-Wide (All Branches, Full Audit Log) |
| **Branch Manager** | `manager@mmi-demo.com` | `Demo@12345` | **Muscat Branch Only** (Server-side enforced RBAC) |
| **Senior Analyst** | `analyst@mmi-demo.com` | `Demo@12345` | Company-Wide Analytics & Audit Inspection |

> **Quick Demo**: The login page provides 1-click demo login buttons for rapid executive walkthroughs.

---

## 🚀 Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm

### 1. Backend Setup
```bash
# Clone repository
git clone https://github.com/mmi-enterprise/mmi-ai-analytics.git
cd mmi_erp

# Create virtual environment & install dependencies
python -m venv venv
venv\Scripts\activate          # On Windows
# source venv/bin/activate     # On macOS/Linux

pip install -r apps/api/requirements.txt

# Run database migrations and deterministic seeder (50,000+ records)
python database/seed/seed_data.py

# Start FastAPI backend server
cd apps/api
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The API is live at `http://127.0.0.1:8000`. Health check: `http://127.0.0.1:8000/api/health`.

### 2. Frontend Setup
In a new terminal window:
```bash
cd apps/web
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🧪 Automated Testing Suite

Run the comprehensive pytest integration test suite covering RBAC branch isolation, SQL injection prevention, Arabic question parsing, reports, and health checks:
```bash
python -m pytest -v
```
**Test Results**: `23 passed in 2.7s` with zero errors.

---

## 🌐 Production Deployment Guide

### Architecture Targets (Free-Tier Ready)
- **Frontend**: [Vercel](https://vercel.com) (Static SPA Build)
- **Backend**: [Render](https://render.com) (FastAPI Web Service)
- **Database**: [Neon](https://neon.tech) (Serverless PostgreSQL)

For complete environment variable configuration, build commands, and step-by-step instructions, see [docs/DEPLOYMENT.md](file:///c:/Users/Home/Downloads/mmi_erp/docs/DEPLOYMENT.md).

---

## 🔒 Security & Privacy Notice
- Database connections run under read-only transaction parameters.
- User passwords are cryptographically hashed using **bcrypt** with salted rounds.
- JWT access tokens use HMAC-SHA256 signatures with configured expiration.
- API keys, database credentials, and secret keys are never committed or exposed to the client.
