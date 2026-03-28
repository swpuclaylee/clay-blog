from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.collect import Collect
from src.repositories.base import BaseRepository


class CollectRepository(BaseRepository[Collect]):
    def __init__(self):
        super().__init__(Collect)

    async def get_by_user_article(
        self, db: AsyncSession, user_id: int, article_id: int
    ) -> Collect | None:
        result = await db.execute(
            select(Collect).where(
                Collect.user_id == user_id, Collect.article_id == article_id
            )
        )
        return result.scalar_one_or_none()

    async def get_page_by_user(
        self, db: AsyncSession, user_id: int, page: int, size: int
    ) -> tuple[list[Collect], int]:
        query = (
            select(Collect)
            .where(Collect.user_id == user_id)
            .order_by(Collect.create_time.desc())
        )
        count_q = (
            select(func.count()).select_from(Collect).where(Collect.user_id == user_id)
        )
        total = (await db.execute(count_q)).scalar() or 0
        items = (
            (await db.execute(query.offset((page - 1) * size).limit(size)))
            .scalars()
            .all()
        )
        return list(items), total

    async def get_admin_page(
        self, db: AsyncSession, page: int, size: int
    ) -> tuple[list[Collect], int]:
        query = select(Collect).order_by(Collect.create_time.desc())
        total = (
            await db.execute(select(func.count()).select_from(Collect))
        ).scalar() or 0
        items = (
            (await db.execute(query.offset((page - 1) * size).limit(size)))
            .scalars()
            .all()
        )
        return list(items), total


collect_repo = CollectRepository()
