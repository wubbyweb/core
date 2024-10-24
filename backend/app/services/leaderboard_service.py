from fastapi import HTTPException
from typing import List, Optional
from datetime import datetime
from ..schemas.leaderboard import (
    ScoreHistoryCreate,
    ScoreUpdateResponse,
    LeaderboardResponse,
    GlobalLeaderboard,
    ChallengeLeaderboard,
    LeaderboardEntry
)
from ..db.supabase_client import supabase
import logging

logger = logging.getLogger(__name__)

class LeaderboardService:
    @staticmethod
    async def get_global_leaderboard_data() -> LeaderboardResponse:
        """Fetch global leaderboard data"""
        try:
            response = supabase.get_global_leaderboard()

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
            logger.error(f"Failed to fetch global leaderboard: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch global leaderboard: {str(e)}"
            )

    @staticmethod
    async def get_challenge_leaderboard(challenge_id: str) -> LeaderboardResponse:
        """Fetch challenge-specific leaderboard data"""
        try:
            response = supabase.get_challenge_leaderboard(challenge_id)

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
            logger.error(f"Failed to fetch challenge leaderboard: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch challenge leaderboard: {str(e)}"
            )

    @staticmethod
    async def update_score(score_data: ScoreHistoryCreate) -> ScoreUpdateResponse:
        """Update user's score for a challenge"""
        try:
            # First, try to get existing score
            existing_score = supabase.select(
                'score_history',
                '*',
                {
                    'challenge_id': score_data.challenge_id,
                    'user_id': score_data.user_id
                }
            )

            # Prepare score data
            score_record = {
                'challenge_id': score_data.challenge_id,
                'user_id': score_data.user_id,
                'score': score_data.score,
                'last_updated': datetime.utcnow().isoformat()
            }

            if existing_score.data:
                # Update existing score if it's higher
                if score_data.score > existing_score.data[0]['score']:
                    response = supabase.update(
                        'score_history',
                        score_record,
                        {
                            'challenge_id': score_data.challenge_id,
                            'user_id': score_data.user_id
                        }
                    )
                else:
                    return ScoreUpdateResponse(
                        success=False,
                        message="New score is not higher than existing score",
                        score=existing_score.data[0]['score'],
                        rank=None
                    )
            else:
                # Insert new score
                response = supabase.insert('score_history', score_record)

            if not response.data:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to update score"
                )

            # Get updated rank
            new_rank = LeaderboardService._calculate_rank(
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
            logger.error(f"Failed to update score: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to update score: {str(e)}"
            )

    @staticmethod
    def _calculate_rank(challenge_id: str, user_id: str) -> Optional[int]:
        """Calculate user's current rank for a challenge"""
        try:
            response = supabase.get_user_challenge_rank(challenge_id, user_id)
            return response.data[0]['rank'] if response.data else None
        except Exception as e:
            logger.error(f"Failed to calculate rank: {str(e)}")
            return None

    @staticmethod
    async def get_user_scores(user_id: str) -> List[dict]:
        """Get all scores for a specific user"""
        try:
            response = supabase.get_user_scores(user_id)
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get user scores: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch user scores: {str(e)}"
            )

    @staticmethod
    async def get_challenge_scores(challenge_id: str) -> List[dict]:
        """Get all scores for a specific challenge"""
        try:
            response = supabase.get_challenge_scores(challenge_id)
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to get challenge scores: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch challenge scores: {str(e)}"
            )

    @staticmethod
    async def delete_score(user_id: str, date: datetime) -> dict:
        """Delete a user's score after a specific date"""
        try:
            response = supabase.delete(
                'score_history',
                {
                    'user_id': user_id,
                    'last_updated': {'gt': date.isoformat()}
                }
            )

            if not response.data:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to delete score"
                )

            return {"message": "Score deleted successfully"}

        except Exception as e:
            logger.error(f"Failed to delete score: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to delete score: {str(e)}"
            )
