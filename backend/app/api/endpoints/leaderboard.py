# backend/app/api/endpoints/leaderboard.py
from fastapi import APIRouter, Depends
from typing import List
from ...schemas.leaderboard import (
    LeaderboardResponse,
    ScoreUpdateResponse,
    ScoreHistoryCreate,
    ChallengeCreate
)
from ...services.leaderboard_service import LeaderboardService

router = APIRouter()

@router.get("/", response_model=LeaderboardResponse)
async def get_global_leaderboard():
    """Get global leaderboard data"""
    return LeaderboardService.get_global_leaderboard_data()

@router.get("/challenge/{challenge_id}", response_model=LeaderboardResponse)
async def get_challenge_leaderboard(challenge_id: str):
    """Get leaderboard for specific challenge"""
    return LeaderboardService.get_leaderboard_info(challenge_id)

@router.post("/challenge/{challenge_id}/score", response_model=ScoreUpdateResponse)
async def update_challenge_score(
    challenge_id: str,
    score_data: ScoreHistoryCreate
):
    """Update score for specific challenge"""
    return LeaderboardService.update_score(challenge_id, score_data)

@router.post("/challenge", response_model=LeaderboardResponse)
async def create_challenge(challenge_data: ChallengeCreate):
    """Create new challenge"""
    return LeaderboardService.create_challenge(challenge_data)