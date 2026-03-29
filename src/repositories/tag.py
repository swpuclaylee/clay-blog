from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.article import ArticleTag
from src.models.tag import Tag
from src.repositories.base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    def __init__(self):
        super().__init__(Tag)

    async def get_all(self, db: AsyncSession) -> list[Tag]:
        result = await db.execute(select(Tag))
        return list(result.scalars().all())

    async def get_by_name(self, db: AsyncSession, name: str) -> Tag | None:
        result = await db.execute(select(Tag).where(Tag.name == name))
        return result.scalar_one_or_none()

    async def get_page(self, db: AsyncSession, page: int, size: int) -> tuple[list[Tag], int]:
        total = (await db.execute(select(func.count()).select_from(Tag))).scalar() or 0
        items = (
            (await db.execute(select(Tag).offset((page - 1) * size).limit(size)))
            .scalars()
            .all()
        )
        return list(items), total

    async def get_by_ids(self, db: AsyncSession, ids: list[int]) -> list[Tag]:
        if not ids:
            return []
        result = await db.execute(select(Tag).where(Tag.id.in_(ids)))
        return list(result.scalars().all())

    async def article_count(self, db: AsyncSession, tag_id: int) -> int:
        result = await db.execute(
            select(func.count()).select_from(ArticleTag).where(ArticleTag.tag_id == tag_id)
        )
        return result.scalar() or 0


tag_repo = TagRepository()
