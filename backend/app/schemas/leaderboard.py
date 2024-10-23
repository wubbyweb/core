# backend/app/schemas/leaderboard.py
from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    id: UUID4

class UserRead(UserBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

class ScoreHistoryBase(BaseModel):
    challenge_id: str
    user_id: UUID4
    score: int
    last_updated: datetime

class ScoreHistoryCreate(ScoreHistoryBase):
    pass

class ScoreHistoryRead(ScoreHistoryBase):
    id: UUID4

    class Config:
        from_attributes = True

class LeaderboardEntryBase(BaseModel):
    username: str
    score: int
    rank: int
    last_updated: datetime

class LeaderboardEntry(LeaderboardEntryBase):
    class Config:
        from_attributes = True

class ChallengeLeaderboard(BaseModel):
    challenge_id: str
    scores: List[LeaderboardEntry]

    class Config:
        from_attributes = True

class GlobalLeaderboard(BaseModel):
    entries: List[LeaderboardEntry]

    class Config:
        from_attributes = True

class ScoreUpdate(BaseModel):
    score: int
    user_id: UUID4

class ChallengeCreate(BaseModel):
    challenge_id: str
    initial_score: Optional[int] = 0

# Response models
class LeaderboardResponse(BaseModel):
    success: bool
    data: GlobalLeaderboard | ChallengeLeaderboard
    message: Optional[str] = None

class ScoreUpdateResponse(BaseModel):
    success: bool
    message: str
    score: Optional[int] = None
    rank: Optional[int] = None