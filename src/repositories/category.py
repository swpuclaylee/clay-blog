from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.article import Article
from src.models.category import Category
from src.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self):
        super().__init__(Category)

    async def get_all(self, db: AsyncSession) -> list[Category]:
        result = await db.execute(select(Category).where(Category.deleted == 0))
        return list(result.scalars().all())

    async def get_by_name(self, db: AsyncSession, name: str) -> Category | None:
        result = await db.execute(
            select(Category).where(Category.name == name, Category.deleted == 0)
        )
        return result.scalar_one_or_none()

    async def get_page(
        self, db: AsyncSession, page: int, size: int
    ) -> tuple[list[Category], int]:
        query = select(Category).where(Category.deleted == 0)
        total = (
            await db.execute(
                select(func.count()).select_from(Category).where(Category.deleted == 0)
            )
        ).scalar()
        items = (
            (await db.execute(query.offset((page - 1) * size).limit(size)))
            .scalars()
            .all()
        )
        return list(items), total

    async def article_count(self, db: AsyncSession, category_id: int) -> int:
        result = await db.execute(
            select(func.count())
            .select_from(Article)
            .where(
                Article.category_id == category_id,
                Article.deleted == 0,
                Article.status == 1,
            )
        )
        return result.scalar() or 0

    async def soft_delete(self, db: AsyncSession, id: int) -> bool:
        obj = await self.get(db, id)
        if not obj:
            return False
        obj.deleted = 1
        await db.commit()
        return True


category_repo = CategoryRepository()
