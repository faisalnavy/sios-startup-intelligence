-- SIOS Supabase Schema
-- Run this in your Supabase SQL Editor (https://app.supabase.com → SQL Editor)

-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- ─────────────────────────────────────────
-- USERS (extends Supabase auth.users)
-- ─────────────────────────────────────────
create table public.users (
  id            uuid references auth.users(id) on delete cascade primary key,
  email         text unique not null,
  full_name     text,
  avatar_url    text,
  credits       integer not null default 1,  -- 1 free credit on signup
  total_reports integer not null default 0,
  created_at    timestamptz default now(),
  updated_at    timestamptz default now()
);

alter table public.users enable row level security;

create policy "Users can view own profile"
  on public.users for select using (auth.uid() = id);

create policy "Users can update own profile"
  on public.users for update using (auth.uid() = id);

-- Auto-create user profile on signup
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.users (id, email, full_name, avatar_url)
  values (
    new.id,
    new.email,
    new.raw_user_meta_data->>'full_name',
    new.raw_user_meta_data->>'avatar_url'
  );
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- ─────────────────────────────────────────
-- ANALYSES
-- ─────────────────────────────────────────
create table public.analyses (
  id            uuid default uuid_generate_v4() primary key,
  user_id       uuid references public.users(id) on delete cascade,
  startup_name  text not null,
  input_data    jsonb not null,
  status        text not null default 'queued',  -- queued | running | completed | error
  verdict       text,                             -- STRONG BUY | BUY WITH CAUTION | etc.
  score         numeric(5,2),
  success_prob  integer,
  is_public     boolean default false,
  share_token   text unique default encode(gen_random_bytes(12), 'hex'),
  created_at    timestamptz default now(),
  completed_at  timestamptz
);

alter table public.analyses enable row level security;

create policy "Users can view own analyses"
  on public.analyses for select using (auth.uid() = user_id or is_public = true);

create policy "Users can insert own analyses"
  on public.analyses for insert with check (auth.uid() = user_id);

create policy "Users can update own analyses"
  on public.analyses for update using (auth.uid() = user_id);

create index idx_analyses_user_id on public.analyses(user_id);
create index idx_analyses_share_token on public.analyses(share_token);

-- ─────────────────────────────────────────
-- REPORTS (full report data)
-- ─────────────────────────────────────────
create table public.reports (
  id               uuid default uuid_generate_v4() primary key,
  analysis_id      uuid references public.analyses(id) on delete cascade unique,
  report_data      jsonb not null,
  pdf_url          text,
  created_at       timestamptz default now()
);

alter table public.reports enable row level security;

create policy "Users can view reports for own analyses"
  on public.reports for select
  using (
    exists (
      select 1 from public.analyses a
      where a.id = analysis_id
      and (a.user_id = auth.uid() or a.is_public = true)
    )
  );

create policy "Service role can insert reports"
  on public.reports for insert with check (true);

-- ─────────────────────────────────────────
-- CREDIT TRANSACTIONS
-- ─────────────────────────────────────────
create table public.credit_transactions (
  id          uuid default uuid_generate_v4() primary key,
  user_id     uuid references public.users(id) on delete cascade,
  amount      integer not null,               -- positive = added, negative = used
  type        text not null,                  -- purchase | usage | bonus | refund
  description text,
  analysis_id uuid references public.analyses(id),
  payment_id  uuid,
  created_at  timestamptz default now()
);

alter table public.credit_transactions enable row level security;

create policy "Users can view own transactions"
  on public.credit_transactions for select using (auth.uid() = user_id);

create index idx_credit_tx_user_id on public.credit_transactions(user_id);

-- ─────────────────────────────────────────
-- PAYMENTS
-- ─────────────────────────────────────────
create table public.payments (
  id              uuid default uuid_generate_v4() primary key,
  user_id         uuid references public.users(id) on delete cascade,
  gateway         text not null,              -- stripe | razorpay
  gateway_id      text unique not null,       -- Stripe payment_intent_id or Razorpay order_id
  amount_usd      numeric(10,2) not null,
  credits_added   integer not null,
  status          text not null default 'pending',  -- pending | completed | failed | refunded
  receipt_url     text,
  metadata        jsonb,
  created_at      timestamptz default now(),
  completed_at    timestamptz
);

alter table public.payments enable row level security;

create policy "Users can view own payments"
  on public.payments for select using (auth.uid() = user_id);

create index idx_payments_user_id on public.payments(user_id);
create index idx_payments_gateway_id on public.payments(gateway_id);

-- ─────────────────────────────────────────
-- HELPER FUNCTIONS
-- ─────────────────────────────────────────

-- Add credits to user
create or replace function public.add_credits(p_user_id uuid, p_amount integer, p_description text, p_payment_id uuid default null)
returns void as $$
begin
  update public.users set credits = credits + p_amount, updated_at = now() where id = p_user_id;
  insert into public.credit_transactions (user_id, amount, type, description, payment_id)
  values (p_user_id, p_amount, 'purchase', p_description, p_payment_id);
end;
$$ language plpgsql security definer;

-- Deduct 1 credit for analysis
create or replace function public.use_credit(p_user_id uuid, p_analysis_id uuid)
returns boolean as $$
declare v_credits integer;
begin
  select credits into v_credits from public.users where id = p_user_id;
  if v_credits < 1 then return false; end if;
  update public.users set credits = credits - 1, total_reports = total_reports + 1, updated_at = now() where id = p_user_id;
  insert into public.credit_transactions (user_id, amount, type, description, analysis_id)
  values (p_user_id, -1, 'usage', 'Report: ' || p_analysis_id, p_analysis_id);
  return true;
end;
$$ language plpgsql security definer;
