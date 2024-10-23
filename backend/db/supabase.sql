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
