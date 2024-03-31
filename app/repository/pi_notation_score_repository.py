from google.cloud import firestore
from ..models import Score
import asyncio
from typing import List

class PiNotationScoreRepository:
    expiration_seconds = 60 * 60 * 24  # 1 days
    match_times_length = 10

    def __init__(self, firestore_db: firestore.AsyncClient) -> None:
        self._db: firestore.AsyncClient = firestore_db

    async def add(self, score: Score) -> None:
        doc_ref = self._db.collection(score.source).document(str(score.timestamp))
        await doc_ref.set(score.model_dump())

    async def delete_scores_before_timestamp(self, source: str, timestamp: int) -> None:
        doc_snapshots = [
            doc_snapshot
            async for doc_snapshot in self._db.collection(source).where("timestamp", "<=", timestamp).stream()
        ]
        await asyncio.gather(
            *(self._db.collection(source).document(doc_snapshot.id).delete() for doc_snapshot in doc_snapshots)
        )

    async def get_scores_larger_than_threshold(self, threshold: float, source: str, limit: int) -> List[Score]:
        return [
            Score(**doc_snapshot.to_dict())
            async for doc_snapshot in self._db.collection(source)
            .where("score", ">", threshold)
            .order_by("score", direction=firestore.Query.DESCENDING)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        ]