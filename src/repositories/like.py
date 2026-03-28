from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.like import Like
from src.repositories.base import BaseRepository


class LikeRepository(BaseRepository[Like]):
    def __init__(self):
        super().__init__(Like)

    async def get_by_user_article(
        self, db: AsyncSession, user_id: int, article_id: int
    ) -> Like | None:
        result = await db.execute(
            select(Like).where(Like.user_id == user_id, Like.article_id == article_id)
        )
        return result.scalar_one_or_none()


like_repo = LikeRepository()
