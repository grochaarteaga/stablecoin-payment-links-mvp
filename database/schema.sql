-- Invoices table
create table if not exists public.invoices (
    id text primary key,
    amount numeric(18, 4) not null,
    currency text not null,
    memo text,
    merchant_wallet text not null,
    status text not null default 'PENDING',
    payment_link text not null,
    created_at timestamptz not null default now()
);

-- Later you can add a users table and foreign key
