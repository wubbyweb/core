from fastapi import APIRouter, HTTPException
from ...services.leaderboard_service import LeaderboardService
from ...schemas.leaderboard import (
    ScoreHistoryCreate,
    ScoreUpdateResponse,
    LeaderboardResponse
)
from datetime import datetime

router = APIRouter()

@router.get("/global", response_model=LeaderboardResponse)
async def get_global_leaderboard():
    """Get global leaderboard across all challenges"""
    return await LeaderboardService.get_global_leaderboard_data()

@router.get("/challenge/{challenge_id}", response_model=LeaderboardResponse)
async def get_challenge_leaderboard(challenge_id: str):
    """Get leaderboard for a specific challenge"""
    return await LeaderboardService.get_challenge_leaderboard(challenge_id)

@router.post("/score", response_model=ScoreUpdateResponse)
async def update_score(
    challenge_id: str,
    user_id: str,
    score: int
):
    """Update a user's score for a challenge"""
    try:
        score_history = ScoreHistoryCreate(
            challenge_id=challenge_id,
            user_id=user_id,
            score=score,
            last_updated=datetime.utcnow()
        )
        return await LeaderboardService.update_score(score_history)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))