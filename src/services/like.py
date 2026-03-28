from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.article import article_repo
from src.repositories.like import like_repo


class LikeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def is_liked(self, user_id: int, article_id: int) -> bool:
        return (
            await like_repo.get_by_user_article(self.db, user_id, article_id)
            is not None
        )

    async def like(self, user_id: int, article_id: int) -> None:
        existing = await like_repo.get_by_user_article(self.db, user_id, article_id)
        if existing:
            return
        await like_repo.create(self.db, {"user_id": user_id, "article_id": article_id})
        article = await article_repo.get(self.db, article_id)
        if article:
            await article_repo.update(
                self.db, article_id, {"like_count": article.like_count + 1}
            )

    async def unlike(self, user_id: int, article_id: int) -> None:
        existing = await like_repo.get_by_user_article(self.db, user_id, article_id)
        if not existing:
            return
        await like_repo.hard_delete(self.db, existing.id)
        article = await article_repo.get(self.db, article_id)
        if article and article.like_count > 0:
            await article_repo.update(
                self.db, article_id, {"like_count": article.like_count - 1}
            )
