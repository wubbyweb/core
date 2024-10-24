# backend/app/schemas/leaderboard.py
from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import List, Optional

# Base Models
class UserBase(BaseModel):
    username: str

class ScoreBase(BaseModel):
    challenge_id: str
    user_id: UUID4
    score: int

# Request Models
class ScoreUpdateRequest(ScoreBase):
    pass

class ChallengeCreate(BaseModel):
    challenge_id: str
    initial_score: Optional[int] = 0

# Response Models
class ScoreUpdateResponse(BaseModel):
    success: bool
    message: str
    score: int
    rank: Optional[int] = None

class LeaderboardEntry(BaseModel):
    username: str
    score: int
    rank: int
    last_updated: datetime

class ChallengeLeaderboard(BaseModel):
    challenge_id: str
    scores: List[LeaderboardEntry]

class GlobalLeaderboard(BaseModel):
    entries: List[LeaderboardEntry]

class LeaderboardResponse(BaseModel):
    success: bool
    data: GlobalLeaderboard | ChallengeLeaderboard
    message: Optional[str] = None

# Internal Models
class ScoreHistoryCreate(ScoreBase):
    last_updated: datetime