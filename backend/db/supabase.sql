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
-- Function to get global leaderboard with materialized view
CREATE MATERIALIZED VIEW global_leaderboard_view AS
SELECT 
    u.username,
    COALESCE(SUM(sh.score), 0) as total_score,
    MAX(sh.last_updated) as last_updated
FROM 
    public.users u
LEFT JOIN 
    score_history sh ON u.id = sh.user_id
GROUP BY 
    u.username
ORDER BY 
    total_score DESC;

-- Create index for better performance
CREATE INDEX idx_global_leaderboard_score 
ON global_leaderboard_view (total_score DESC);

-- Function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_global_leaderboard()
RETURNS trigger AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY global_leaderboard_view;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to refresh view when scores change
CREATE TRIGGER refresh_global_leaderboard_trigger
AFTER INSERT OR UPDATE OR DELETE ON score_history
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_global_leaderboard();

-- Function to get global leaderboard
CREATE OR REPLACE FUNCTION get_global_leaderboard()
RETURNS TABLE (
    username text,
    score bigint,
    last_updated timestamp with time zone
) LANGUAGE sql STABLE AS $$
    SELECT 
        username,
        total_score as score,
        last_updated
    FROM 
        global_leaderboard_view
    ORDER BY 
        total_score DESC;
$$;

-- Function to get challenge leaderboard
CREATE OR REPLACE FUNCTION get_challenge_leaderboard(challenge_id_param text)
RETURNS TABLE (
    username text,
    score int,
    last_updated timestamp with time zone
) LANGUAGE sql STABLE AS $$
    WITH latest_scores AS (
        SELECT DISTINCT ON (user_id)
            user_id,
            score,
            last_updated
        FROM 
            score_history
        WHERE 
            challenge_id = challenge_id_param
        ORDER BY 
            user_id, last_updated DESC
    )
    SELECT 
        u.username,
        ls.score,
        ls.last_updated
    FROM 
        latest_scores ls
    JOIN 
        users u ON u.id = ls.user_id
    ORDER BY 
        ls.score DESC;
$$;