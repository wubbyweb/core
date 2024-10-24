from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LeaderboardEntry(BaseModel):
    username: str
    score: int
    rank: int
    last_updated: datetime

class GlobalLeaderboard(BaseModel):
    entries: List[LeaderboardEntry]

class ChallengeLeaderboard(BaseModel):
    challenge_id: str
    scores: List[LeaderboardEntry]

class LeaderboardResponse(BaseModel):
    success: bool
    data: GlobalLeaderboard | ChallengeLeaderboard

class ScoreHistoryCreate(BaseModel):
    challenge_id: str
    user_id: str
    score: int
    last_updated: datetime

class ScoreUpdateResponse(BaseModel):
    success: bool
    message: str
    score: int
    rank: Optional[int]