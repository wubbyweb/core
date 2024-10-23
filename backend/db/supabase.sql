-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own profile" ON users;
DROP POLICY IF EXISTS "Users can insert own profile" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;

-- Create policies for users table
CREATE POLICY "Users can view own profile" ON users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON users
  FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
  FOR UPDATE USING (auth.uid() = id);

-- Allow public access for user registration
CREATE POLICY "Allow public insert for registration" ON users
  FOR INSERT WITH CHECK (true);



-- Leaderboard statement and functions


-- This is typically created automatically by Supabase Auth
create table public.users (
    id uuid references auth.users primary key, -- Links to Supabase Auth
    username text unique not null,
    created_at timestamp with time zone default timezone('utc'::text, now())
    -- other user fields...
);

-- Score history table
create table public.score_history (
    id uuid default uuid_generate_v4() primary key,
    challenge_id text not null,
    user_id uuid references public.users not null,
    score integer not null,
    last_updated timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Function to get latest global scores
create or replace function get_latest_global_scores()
returns table (
    username text,
    score integer,
    last_updated timestamp with time zone
) language sql as $$
    with latest_scores as (
        select 
            user_id,
            score,
            last_updated,
            row_number() over (
                partition by user_id 
                order by last_updated desc
            ) as rn
        from score_history
    )
    select 
        u.username,
        ls.score,
        ls.last_updated
    from latest_scores ls
    inner join users u on u.id = ls.user_id
    where ls.rn = 1
    order by ls.score desc;
$$;

-- Function to get latest challenge scores
create or replace function get_latest_challenge_scores(challenge_id_param text)
returns table (
    username text,
    score integer,
    last_updated timestamp with time zone
) language sql as $$
    with latest_scores as (
        select 
            user_id,
            score,
            last_updated,
            row_number() over (
                partition by user_id 
                order by last_updated desc
            ) as rn
        from score_history
        where challenge_id = challenge_id_param
    )
    select 
        u.username,
        ls.score,
        ls.last_updated
    from latest_scores ls
    inner join users u on u.id = ls.user_id
    where ls.rn = 1
    order by ls.score desc;
$$;
-- Function to get user's rank in a challenge
create or replace function get_user_challenge_rank(
    challenge_id_param text,
    user_id_param uuid
)
returns table (
    rank bigint
) language sql as $$
    with latest_scores as (
        select 
            user_id,
            score,
            last_updated,
            row_number() over (
                partition by user_id 
                order by last_updated desc
            ) as rn
        from score_history
        where challenge_id = challenge_id_param
    ),
    ranked_scores as (
        select 
            user_id,
            score,
            row_number() over (order by score desc) as rank
        from latest_scores
        where rn = 1
    )
    select rank
    from ranked_scores
    where user_id = user_id_param;
$$;