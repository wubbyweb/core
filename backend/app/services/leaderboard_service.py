# backend/app/services/leaderboard_service.py
from typing import Dict, List, Optional
from datetime import datetime
import json
from redis import Redis
from fastapi import HTTPException
from supabase import create_client, Client
from ..core.config import settings
from ..schemas.leaderboard import (
    LeaderboardEntry,
    GlobalLeaderboard,
    ChallengeLeaderboard,
    ScoreHistoryCreate,
    ScoreUpdateResponse,
    LeaderboardResponse
)

class LeaderboardService:
    @staticmethod
    def get_global_leaderboard_data() -> LeaderboardResponse:
        """Fetch latest global leaderboard data with caching"""
        cached_data = redis_client.get("global_leaderboard")
        if cached_data:
            return LeaderboardResponse(
                success=True,
                data=GlobalLeaderboard.model_validate_json(cached_data)
            )

        try:
            response = supabase.rpc('get_latest_global_scores').execute()

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

            redis_client.setex(
                "global_leaderboard",
                CACHE_EXPIRY,
                leaderboard_data.model_dump_json()
            )

            return LeaderboardResponse(
                success=True,
                data=leaderboard_data
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch leaderboard: {str(e)}"
            )

    @staticmethod
    def get_leaderboard_info(challenge_id: str) -> LeaderboardResponse:
        """Get latest leaderboard information for a specific challenge"""
        cache_key = f"challenge_leaderboard:{challenge_id}"

        cached_data = redis_client.get(cache_key)
        if cached_data:
            return LeaderboardResponse(
                success=True,
                data=ChallengeLeaderboard.model_validate_json(cached_data)
            )

        try:
            response = supabase.rpc(
                'get_latest_challenge_scores',
                {'challenge_id_param': challenge_id}
            ).execute()

            if not response.data:
                raise HTTPException(status_code=404, detail="Challenge not found")

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

            redis_client.setex(
                cache_key,
                CACHE_EXPIRY,
                leaderboard_data.model_dump_json()
            )

            return LeaderboardResponse(
                success=True,
                data=leaderboard_data
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch challenge leaderboard: {str(e)}"
            )

    @staticmethod
    def update_score(challenge_id: str, score_data: ScoreHistoryCreate) -> ScoreUpdateResponse:
        """Insert new score record for a specific challenge"""
        try:
            data = score_data.model_dump()

            response = supabase.from_('score_history')\
                .insert(data)\
                .execute()

            if not response.data:
                raise HTTPException(status_code=404, detail="Failed to update score")

            # Invalidate related caches
            redis_client.delete(f"challenge_leaderboard:{challenge_id}")
            redis_client.delete("global_leaderboard")

            # Get updated rank
            new_rank = LeaderboardService._calculate_rank(
                challenge_id, 
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
    def _calculate_rank(challenge_id: str, user_id: str) -> int:
        """Calculate user's current rank for a specific challenge"""
        try:
            response = supabase.rpc(
                'get_user_challenge_rank',
                {
                    'challenge_id_param': challenge_id,
                    'user_id_param': user_id
                }
            ).execute()

            return response.data[0]['rank'] if response.data else None
        except Exception:
            return None