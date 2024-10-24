import httpx
import asyncio
import uuid
from datetime import datetime

# Base URL - replace with your actual API base URL
BASE_URL = "https://6dfcc545-5499-4451-82f8-3e6dc2cf4afa-00-1k6jvenqc5aos.worf.replit.dev"

async def test_leaderboard_endpoints():
    async with httpx.AsyncClient() as client:
        # Test global leaderboard endpoint
        print("\nTesting Global Leaderboard...")
        response = await client.get(f"{BASE_URL}/leaderboard/global")
        print(f"Status: {response.status_code}")
        print("Response:", response.json())

        # Test challenge leaderboard endpoint
        challenge_id = "test-challenge-1"  # Replace with actual challenge ID
        print(f"\nTesting Challenge Leaderboard for {challenge_id}...")
        response = await client.get(f"{BASE_URL}/leaderboard/challenge/{challenge_id}")
        print(f"Status: {response.status_code}")
        print("Response:", response.json())

        # Test score update endpoint
        print("\nTesting Score Update...")
        score_data = {
            "challenge_id": challenge_id,
            "user_id": str(uuid.uuid4()),  # Generate random UUID for testing
            "score": 100
        }

        print(score_data)
        response = await client.post(f"{BASE_URL}/leaderboard/score", json=score_data)
        print(f"Status: {response.status_code}")
        print("Response:", response.json())

        # Test score delete endpoint
        print("\nTesting Score Delete...")
        user_id = str(uuid.uuid4())  # Generate random UUID for testing
        date = datetime.utcnow().isoformat()
        response = await client.delete(f"{BASE_URL}/leaderboard/score", params={"user_id": user_id, "date": date})
        print(f"Status: {response.status_code}")
        print("Response:", response.json())

if __name__ == "__main__":
    asyncio.run(test_leaderboard_endpoints())
