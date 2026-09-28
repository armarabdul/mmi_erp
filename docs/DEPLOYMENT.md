# Deployment Guide — MMI AI Analytics

This guide describes how to deploy MMI AI Analytics to production on free-tier platforms:
- **Frontend**: Vercel
- **Backend API**: Render (Web Service)
- **Database**: Neon (PostgreSQL)

---

## 1. Database Setup (Neon PostgreSQL)

1. Sign up for a free account at [Neon.tech](https://neon.tech).
2. Create a new project: `mmi-analytics`.
3. Copy the PostgreSQL connection string:
   ```
   postgresql://mmi_user:<PASSWORD>@<HOST>/mmi_analytics?sslmode=require
   ```
4. Run migrations and the deterministic seed script against Neon:
   ```bash
   export DATABASE_URL="postgresql://mmi_user:<PASSWORD>@<HOST>/mmi_analytics?sslmode=require"
   python database/seed/seed_data.py
   ```
   This will seed all 4 branches, products, demo users, and 50,000+ sales records deterministically.

---

## 2. Backend Deployment (Render)

1. Sign up at [Render.com](https://render.com) and create a **New Web Service**.
2. Connect your GitHub repository.
3. Configure the service settings:
   - **Root Directory**: `apps/api`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set Environment Variables in Render:
   - `DATABASE_URL`: Your Neon PostgreSQL connection URL.
   - `JWT_SECRET`: A secure 64-character random string.
   - `AI_PROVIDER`: `openai`
   - `OPENAI_API_KEY`: Your OpenAI API key (optional; if omitted, the built-in deterministic KPI analytics engine responds).
   - `OPENAI_MODEL`: `gpt-4o-mini`
   - `CORS_ORIGINS`: `https://your-app.vercel.app`
5. Click **Deploy**. Note your service URL (e.g., `https://mmi-api.onrender.com`).
6. Test health check:
   ```bash
   curl https://mmi-api.onrender.com/api/health
   ```

---

## 3. Frontend Deployment (Vercel)

1. Sign up at [Vercel.com](https://vercel.com) and click **Add New Project**.
2. Import your GitHub repository.
3. Set project settings:
   - **Root Directory**: `apps/web`
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add Environment Variable:
   - `VITE_API_BASE_URL`: `https://mmi-api.onrender.com/api/v1`
5. Click **Deploy**.

---

## 4. Post-Deployment Verification Checklist

- [ ] Open frontend URL: `https://your-app.vercel.app`
- [ ] Test 1-click Admin Login (`admin@mmi-demo.com` / `Demo@12345`)
- [ ] Verify Dashboard KPIs are loaded from Neon PostgreSQL database
- [ ] Navigate to AI Analytics and submit: `Show me sales by branch this month`
- [ ] Switch language to Arabic and submit: `ما هي المبيعات حسب الفرع هذا الشهر؟`
- [ ] Logout and login as Branch Manager (`manager@mmi-demo.com` / `Demo@12345`)
- [ ] Verify Branch Manager sees only Muscat branch data
- [ ] Open Reports, click `Sales by Branch`, and test Excel export download
- [ ] Open Audit Log and verify analytics records
