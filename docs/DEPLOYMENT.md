# PULSAR AI V2.0 — CLOUD DEPLOYMENT GUIDE

This guide provides simple, step-by-step instructions for deploying PULSAR AI V2.0 to your cloud infrastructure.

**No local Python, Node.js, or Docker Desktop is required on your computer.** All production workloads run in the cloud.

---

## Architecture Overview
- **GitHub Repository**: Source code repository.
- **Supabase**: Managed PostgreSQL database, migrations, and Row Level Security.
- **Railway**: Backend FastAPI container and background scheduled scanning worker.
- **Vercel**: Next.js 14 frontend dashboard CDN.

---

## Step 1: Upload Source Code to GitHub

1. Open your browser and navigate to your GitHub repository:
   `https://github.com/alamgirhossain8918-dotcom/pulsar-ai`
2. Ensure all files from the `pulsar-ai` directory are committed and pushed to the `main` branch.

---

## Step 2: Set Up Supabase Database

1. Log in to your [Supabase Dashboard](https://supabase.com/dashboard).
2. Create a new project named `pulsar-ai-db` (or select your existing project).
3. In the left menu, click **SQL Editor**.
4. Open the file `supabase/migrations/20261103_init_pulsar_schema.sql` from your project folder.
5. Copy the entire SQL content, paste it into the Supabase SQL Editor, and click **Run**.
6. Next, open `supabase/seed.sql`, paste its content into the SQL Editor, and click **Run**.
7. In the left menu, go to **Project Settings** -> **Database**.
8. Under **Connection String**, copy the **URI** connection string.
   - Replace `[YOUR-PASSWORD]` with your Supabase database password.
   - Example: `postgresql://postgres:your_password@db.xyz.supabase.co:5432/postgres`

---

## Step 3: Deploy Backend on Railway

1. Log in to your [Railway Dashboard](https://railway.app).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select `alamgirhossain8918-dotcom/pulsar-ai`.
4. In the service settings:
   - **Root Directory**: Leave as `/` or set to `.`
   - **Dockerfile Path**: Set to `backend/Dockerfile`
5. Go to the **Variables** tab and add these environment variables:
   ```env
   PORT=8000
   ENVIRONMENT=production
   DEBUG=false
   SECRET_KEY=generate_a_random_64_character_key_here
   DATABASE_URL=postgresql+asyncpg://postgres:your_password@db.your_project_ref.supabase.co:5432/postgres
   DATABASE_SYNC_URL=postgresql://postgres:your_password@db.your_project_ref.supabase.co:5432/postgres
   PRIMARY_DATA_PROVIDER=binance
   FALLBACK_DATA_PROVIDER=bybit
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_optional
   TELEGRAM_CHAT_ID=your_telegram_chat_id_optional
   TELEGRAM_ALERTS_ENABLED=true
   ```
6. In **Settings**, click **Generate Domain** (e.g. `pulsar-ai-production.up.railway.app`).
7. Save. Railway will automatically build the container and start both the FastAPI server and the continuous background scanner worker.
8. Verify deployment by visiting `https://your-domain.up.railway.app/api/v1/health` in your browser.

---

## Step 4: Deploy Frontend on Vercel

1. Log in to your [Vercel Dashboard](https://vercel.com).
2. Click **Add New** -> **Project**.
3. Import your GitHub repository: `pulsar-ai`.
4. In **Project Configuration**:
   - **Framework Preset**: Next.js
   - **Root Directory**: Click `Edit` and select `frontend`
5. Under **Environment Variables**, add:
   ```env
   NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app/api/v1
   NEXT_PUBLIC_WS_URL=wss://your-railway-app.up.railway.app/api/v1/ws
   NEXT_PUBLIC_SUPABASE_URL=https://your_project_ref.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```
6. Click **Deploy**. Vercel will build and deploy your Next.js application worldwide on its edge network.

---

## Step 5: Verification & Launch

1. Open your Vercel deployment URL (e.g. `https://pulsar-ai.vercel.app`).
2. Verify that:
   - Priority asset prices (BTC, ETH, SOL) update in real-time.
   - Market data provider indicates `BINANCE USDⓈ-M` or `BYBIT`.
   - The Live Scanner shows market structures and regimes.
   - The Backtester and Paper Trading simulator execute properly.
