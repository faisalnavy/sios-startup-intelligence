# SIOS Deployment Guide
# Everything automated except 5 minutes of clicks — all values pre-filled below.

## What's Already Done ✅
- Code pushed to GitHub: https://github.com/faisalnavy/sios-startup-intelligence
- Supabase project created & schema applied: https://fbqeuighcvlkhnlwtwce.supabase.co
- Netlify site created: https://sios-startup-intelligence.netlify.app (env vars set)

---

## Step 1 — Railway (Backend) 🚂

1. Go to https://railway.com → **New Project** → **Deploy from GitHub repo**
2. Select repo: `faisalnavy/sios-startup-intelligence`
3. Set **Root Directory**: `backend`
4. Click **Add Variables** and paste all env vars from the box below
5. Railway will auto-detect `railway.toml` and deploy. Takes ~2 min.

### Railway Environment Variables (copy-paste all):

> **All actual key values are saved locally in `railway-env.txt`** (gitignored).
> Copy from that file into Railway. Below is the template:

```
ANTHROPIC_API_KEY=<from railway-env.txt>
OPENAI_API_KEY=<from railway-env.txt>
TAVILY_API_KEY=<from railway-env.txt>
SUPABASE_URL=https://fbqeuighcvlkhnlwtwce.supabase.co
SUPABASE_ANON_KEY=<from railway-env.txt>
SUPABASE_SERVICE_ROLE_KEY=<get from Supabase: Settings → API → service_role key>
SUPABASE_JWT_SECRET=<get from Supabase: Settings → API → JWT Settings → JWT Secret>
FRONTEND_URL=https://sios-startup-intelligence.netlify.app
CORS_ORIGINS=https://sios-startup-intelligence.netlify.app,http://localhost:3000
PORT=8000
```

**Optional (add later for payments & email):**
```
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_5=price_...
STRIPE_PRICE_20=price_...
STRIPE_PRICE_50=price_...
RESEND_API_KEY=re_...
FROM_EMAIL=noreply@yourdomain.com
```

6. After deploy, copy the Railway URL (e.g. `https://sios-backend.up.railway.app`)

---

## Step 2 — Netlify (Frontend) 🌐

The Netlify site `sios-startup-intelligence.netlify.app` is created with Supabase env vars set.

### Connect GitHub for auto-deploy:
1. Go to https://app.netlify.com/projects/sios-startup-intelligence
2. Click **Site configuration** → **Build & deploy** → **Link repository**
3. Choose **GitHub** → select `faisalnavy/sios-startup-intelligence`
4. Set **Base directory**: `frontend`
5. Set **Build command**: `npm run build`
6. Set **Publish directory**: `.next`
7. Add **one more env var**:
   ```
   NEXT_PUBLIC_API_URL=<paste Railway URL from Step 1>
   ```
8. Click **Deploy site**

---

## Step 3 — Supabase (OAuth Providers) 🔐

1. Go to https://supabase.com/dashboard/project/fbqeuighcvlkhnlwtwce/auth/providers
2. Enable **Google**: needs Google OAuth Client ID + Secret (from console.cloud.google.com)
3. Enable **Microsoft**: needs Azure App Registration (from portal.azure.com)
4. Enable **Facebook**: needs Facebook App ID + Secret (from developers.facebook.com)
5. Set redirect URL: `https://sios-startup-intelligence.netlify.app/auth/callback`

---

## Step 4 — Update Supabase backend .env ⚙️

Copy the service role key and JWT secret from Supabase dashboard:
1. Go to https://supabase.com/dashboard/project/fbqeuighcvlkhnlwtwce/settings/api
2. Copy **service_role** key → add to Railway env vars as `SUPABASE_SERVICE_ROLE_KEY`
3. Copy **JWT Secret** → add to Railway env vars as `SUPABASE_JWT_SECRET`

---

## URLs Summary
| Service | URL |
|---------|-----|
| Frontend | https://sios-startup-intelligence.netlify.app |
| Backend | <Railway URL — set after Step 1> |
| Supabase | https://fbqeuighcvlkhnlwtwce.supabase.co |
| GitHub | https://github.com/faisalnavy/sios-startup-intelligence |

---

## Local Dev
```bash
# Backend
cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt
python main.py  # runs at http://localhost:8000

# Frontend
cd frontend && npm install && npm run dev  # runs at http://localhost:3000
```
