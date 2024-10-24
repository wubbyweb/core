# backend/app/api/endpoints/leaderboard.py
from fastapi import APIRouter, HTTPException
from datetime import datetime
from ...schemas.leaderboard import (
    ScoreUpdateRequest,
    ScoreUpdateResponse,
    LeaderboardResponse,
    ScoreHistoryCreate
)
from ...services.leaderboard_service import LeaderboardService

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

@router.get("/global", response_model=LeaderboardResponse)
async def get_global_leaderboard():
    """Get global leaderboard rankings"""
    return LeaderboardService.get_global_leaderboard_data()

@router.get("/challenge/{challenge_id}", response_model=LeaderboardResponse)
async def get_challenge_leaderboard(challenge_id: str):
    """Get leaderboard for a specific challenge"""
    return LeaderboardService.get_challenge_leaderboard(challenge_id)

@router.post("/score", response_model=ScoreUpdateResponse)
async def update_score(score_data: ScoreUpdateRequest):
    """
    Update a user's score for a specific challenge

    Parameters:
        score_data: ScoreUpdateRequest containing:
            - user_id: UUID of the user
            - challenge_id: ID of the challenge
            - score: New score value
    """
    score_history = ScoreHistoryCreate(
        **score_data.model_dump(),
        last_updated=datetime.utcnow()
    )
    return LeaderboardService.update_score(score_history)