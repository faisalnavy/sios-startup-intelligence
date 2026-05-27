# SIOS — Startup Intelligence Operating System

A full-stack **SaaS web application** that analyzes any startup using **8 specialized AI agents** with **dual Claude + OpenAI cross-validation**, delivering a McKinsey-grade intelligence report in under 5 minutes.

## Features

- **8 AI Agents** running in parallel (market, VC, competitor, financial, risk, feasibility, trend, scoring)
- **Dual-AI Cross-Validation** — Claude analyzes, GPT-4 critiques, Claude synthesizes
- **Real-time Progress** — live SSE streaming with animated progress bar
- **PDF Reports** — beautiful browser-print PDF with all 12 sections
- **Supabase Auth** — Google, Microsoft, Facebook OAuth sign-in
- **Credit System** — $5 minimum / $1 per report via Stripe checkout
- **Dashboard** — analysis history, credit balance, billing, usage analytics
- **Country Feasibility** — SEBI, RBI, and global regulatory analysis

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python) |
| AI Engine 1 | Claude claude-sonnet-4-6 (Anthropic) |
| AI Engine 2 | OpenAI GPT-4o |
| Web Search | Tavily API |
| Frontend | Next.js 15 + TypeScript + TailwindCSS |
| Auth & DB | Supabase (Postgres + Auth + RLS) |
| Payments | Stripe Checkout |
| Email | Resend |
| Real-time | Server-Sent Events (SSE) |

## Local Development

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

Required keys for basic functionality:
```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

Start the backend:
```bash
python main.py
# or double-click SIOS/start_backend.bat on Windows
```

API runs at http://localhost:8000 · Health: http://localhost:8000/api/health

### 2. Frontend Setup

```bash
cd frontend
npm install
```

Edit `frontend/.env.local` — for local dev without Supabase, leave the placeholder values as-is:
```
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=YOUR_ANON_KEY
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_KEY
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the frontend:
```bash
npm run dev
# or double-click SIOS/start_frontend.bat
```

App runs at http://localhost:3000

> **Local dev note**: Without real Supabase credentials, auth and credits are disabled but the AI analysis still works — just go to `/dashboard/new` directly.

---

## Full SaaS Setup (Production)

### Step 1 — Supabase

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run `backend/supabase_schema.sql`
3. Enable **Auth Providers**: Google, Microsoft (Azure), Facebook in Auth > Providers
4. Set redirect URL: `https://your-domain.com/auth/callback`
5. Copy your **Project URL** and **anon key** to frontend `.env.local`
6. Copy your **JWT Secret** (Settings > API) to backend `.env` as `SUPABASE_JWT_SECRET`

### Step 2 — Stripe

1. Create products and prices in [Stripe Dashboard](https://dashboard.stripe.com)
   - Starter: $5 one-time
   - Popular: $20 one-time
   - Pro: $50 one-time
2. Copy the Price IDs to backend `.env`:
   ```
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_PRICE_5=price_...
   STRIPE_PRICE_20=price_...
   STRIPE_PRICE_50=price_...
   ```
3. Create a webhook endpoint pointing to `https://your-api.com/api/payments/webhook/stripe`
   - Listen for: `checkout.session.completed`
4. Copy webhook secret to `STRIPE_WEBHOOK_SECRET`

### Step 3 — Deploy Backend (Railway)

1. Push your code to GitHub
2. Create a new project at [railway.app](https://railway.app)
3. Connect your GitHub repo, select the `backend/` directory (or set root to `backend/`)
4. Add all env variables from your `.env` file
5. Railway auto-detects `railway.toml` and starts the server
6. Copy your Railway URL (e.g. `https://sios-backend.up.railway.app`)

### Step 4 — Deploy Frontend (Vercel)

1. Create a project at [vercel.com](https://vercel.com)
2. Connect your GitHub repo, set **Root Directory** to `frontend/`
3. Add environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://sios-backend.up.railway.app
   NEXT_PUBLIC_SUPABASE_URL=https://xyz.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
   ```
4. Vercel auto-detects `vercel.json` and deploys

### Step 5 — Add Domain

1. In Vercel: add your custom domain (e.g. `sios.yourbrand.com`)
2. Update `FRONTEND_URL` in Railway environment to match your domain
3. Update Supabase redirect URLs to include your domain
4. Update Stripe webhook endpoint URL

---

## Routes

| Route | Description |
|---|---|
| `/` | Landing page |
| `/login` | Sign in with Google / Microsoft / Facebook |
| `/dashboard` | Analysis history overview |
| `/dashboard/new` | Submit new startup analysis |
| `/dashboard/credits` | Buy credits via Stripe |
| `/dashboard/billing` | Payment history |
| `/dashboard/usage` | Usage analytics |
| `/analysis/[id]` | Real-time analysis + report + PDF download |
| `/share/[token]` | Public shareable report |
| `/auth/callback` | OAuth redirect handler |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| POST | `/api/analyze` | Start analysis (1 credit) |
| GET | `/api/analysis/{id}/stream` | SSE progress stream |
| GET | `/api/analysis/{id}/report` | Get completed report |
| GET | `/api/user/profile` | User profile |
| GET | `/api/user/credits` | Credit balance |
| GET | `/api/user/analyses` | Analysis history |
| GET | `/api/payments/packs` | Credit pack catalog |
| POST | `/api/payments/checkout` | Create Stripe session |
| POST | `/api/payments/webhook/stripe` | Stripe webhook |
| GET | `/api/payments/history` | Payment history |
| GET | `/api/share/{token}` | Public report |

## Environment Variables Reference

### Backend `.env`
```
# Required
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

# Supabase (optional for local dev)
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_JWT_SECRET=your-jwt-secret

# Stripe (for payments)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_5=price_...
STRIPE_PRICE_20=price_...
STRIPE_PRICE_50=price_...

# Email (Resend)
RESEND_API_KEY=re_...
FROM_EMAIL=noreply@yourdomain.com

# App
FRONTEND_URL=https://yourdomain.com
CORS_ORIGINS=https://yourdomain.com,http://localhost:3000
```

### Frontend `.env.local`
```
NEXT_PUBLIC_SUPABASE_URL=https://xyz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
NEXT_PUBLIC_API_URL=https://sios-backend.up.railway.app
```
