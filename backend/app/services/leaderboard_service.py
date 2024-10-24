# backend/app/services/leaderboard_service.py
from fastapi import HTTPException
from datetime import datetime
from typing import List, Optional
from ..schemas.leaderboard import (
    ScoreHistoryCreate,
    ScoreUpdateResponse,
    LeaderboardResponse,
    GlobalLeaderboard,
    ChallengeLeaderboard,
    LeaderboardEntry
)
from ..db.supabase_client import supabase

class LeaderboardService:
    @staticmethod
    async def get_global_leaderboard_data() -> LeaderboardResponse:
        """Fetch global leaderboard data"""
        try:
            response = await supabase.rpc('get_global_leaderboard').execute()

            if not response.data:
                return LeaderboardResponse(
                    success=True,
                    data=GlobalLeaderboard(entries=[])
                )

            entries = [
                LeaderboardEntry(
                    username=entry['username'],
                    score=entry['score'],
                    rank=idx + 1,
                    last_updated=entry['last_updated']
                )
                for idx, entry in enumerate(response.data)
            ]

            leaderboard_data = GlobalLeaderboard(entries=entries)
            return LeaderboardResponse(success=True, data=leaderboard_data)

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch global leaderboard: {str(e)}"
            )

    @staticmethod
    async def get_challenge_leaderboard(challenge_id: str) -> LeaderboardResponse:
        """Fetch challenge-specific leaderboard data"""
        try:
            response = await supabase.rpc(
                'get_challenge_leaderboard',
                {'challenge_id_param': challenge_id}
            ).execute()

            if not response.data:
                return LeaderboardResponse(
                    success=True,
                    data=ChallengeLeaderboard(
                        challenge_id=challenge_id,
                        scores=[]
                    )
                )

            scores = [
                LeaderboardEntry(
                    username=entry['username'],
                    score=entry['score'],
                    rank=idx + 1,
                    last_updated=entry['last_updated']
                )
                for idx, entry in enumerate(response.data)
            ]

            leaderboard_data = ChallengeLeaderboard(
                challenge_id=challenge_id,
                scores=scores
            )

            return LeaderboardResponse(success=True, data=leaderboard_data)

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch challenge leaderboard: {str(e)}"
            )

    @staticmethod
    async def update_score(score_data: ScoreHistoryCreate) -> ScoreUpdateResponse:
        """Update user's score for a challenge"""
        try:
            # Insert new score record
            response = await supabase.from_('score_history').insert(
                score_data.model_dump()
            ).execute()

            if not response.data:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to update score"
                )

            # Calculate new rank
            new_rank = await LeaderboardService._calculate_rank(
                score_data.challenge_id,
                score_data.user_id
            )

            return ScoreUpdateResponse(
                success=True,
                message="Score updated successfully",
                score=score_data.score,
                rank=new_rank
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to update score: {str(e)}"
            )

    @staticmethod
    async def _calculate_rank(challenge_id: str, user_id: str) -> Optional[int]:
        """Calculate user's current rank for a challenge"""
        try:
            response = await supabase.rpc(
                'get_user_challenge_rank',
                {
                    'challenge_id_param': challenge_id,
                    'user_id_param': str(user_id)
                }
            ).execute()

            return response.data[0]['rank'] if response.data else None
        except Exception:
            return None

# Create a singleton instance
leaderboard_service = LeaderboardService()