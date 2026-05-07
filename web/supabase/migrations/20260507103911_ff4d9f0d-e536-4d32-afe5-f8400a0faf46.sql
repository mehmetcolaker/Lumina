-- user_stats table for leveling/leaderboard
create table public.user_stats (
  id uuid primary key references auth.users(id) on delete cascade,
  xp integer not null default 0,
  level integer not null default 1,
  streak_days integer not null default 0,
  completed_courses integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.user_stats enable row level security;

create policy "Stats are viewable by everyone"
  on public.user_stats for select using (true);

create policy "Users can insert their own stats"
  on public.user_stats for insert with check (auth.uid() = id);

create policy "Users can update their own stats"
  on public.user_stats for update using (auth.uid() = id);

create trigger trg_user_stats_updated_at
  before update on public.user_stats
  for each row execute function public.set_updated_at();

-- Extend handle_new_user to also create stats row
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, display_name, avatar_url)
  values (
    new.id,
    coalesce(new.raw_user_meta_data ->> 'display_name', new.raw_user_meta_data ->> 'full_name', split_part(new.email, '@', 1)),
    new.raw_user_meta_data ->> 'avatar_url'
  );
  insert into public.user_stats (id) values (new.id);
  return new;
end;
$$;

-- Ensure trigger exists on auth.users
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- Backfill stats for any existing users
insert into public.user_stats (id)
select id from auth.users
where id not in (select id from public.user_stats);