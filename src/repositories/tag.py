from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.article import ArticleTag
from src.models.tag import Tag
from src.repositories.base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    def __init__(self):
        super().__init__(Tag)

    async def get_all(self, db: AsyncSession) -> list[Tag]:
        result = await db.execute(select(Tag).where(Tag.deleted == 0))
        return list(result.scalars().all())

    async def get_by_name(self, db: AsyncSession, name: str) -> Tag | None:
        result = await db.execute(select(Tag).where(Tag.name == name, Tag.deleted == 0))
        return result.scalar_one_or_none()

    async def get_page(
        self, db: AsyncSession, page: int, size: int
    ) -> tuple[list[Tag], int]:
        query = select(Tag).where(Tag.deleted == 0)
        total = (
            await db.execute(
                select(func.count()).select_from(Tag).where(Tag.deleted == 0)
            )
        ).scalar()
        items = (
            (await db.execute(query.offset((page - 1) * size).limit(size)))
            .scalars()
            .all()
        )
        return list(items), total

    async def get_by_ids(self, db: AsyncSession, ids: list[int]) -> list[Tag]:
        if not ids:
            return []
        result = await db.execute(select(Tag).where(Tag.id.in_(ids), Tag.deleted == 0))
        return list(result.scalars().all())

    async def article_count(self, db: AsyncSession, tag_id: int) -> int:
        result = await db.execute(
            select(func.count())
            .select_from(ArticleTag)
            .where(ArticleTag.tag_id == tag_id)
        )
        return result.scalar() or 0

    async def soft_delete(self, db: AsyncSession, id: int) -> bool:
        obj = await self.get(db, id)
        if not obj:
            return False
        obj.deleted = 1
        await db.commit()
        return True


tag_repo = TagRepository()
