from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.category import category_repo
from src.schemas.category import CategoryItem
from src.schemas.common import PageResult


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(self) -> list[CategoryItem]:
        items = await category_repo.get_all(self.db)
        result = []
        for c in items:
            count = await category_repo.article_count(self.db, c.id)
            result.append(
                CategoryItem(
                    id=c.id, name=c.name, description=c.description, articleCount=count
                )
            )
        return result

    async def get_page(self, page: int, size: int) -> PageResult[CategoryItem]:
        items, total = await category_repo.get_page(self.db, page, size)
        pages = (total + size - 1) // size
        result = []
        for c in items:
            count = await category_repo.article_count(self.db, c.id)
            result.append(
                CategoryItem(
                    id=c.id, name=c.name, description=c.description, articleCount=count
                )
            )
        return PageResult(items=result, total=total, page=page, size=size, pages=pages)

    async def create(self, name: str, description: str | None) -> bool:
        existing = await category_repo.get_by_name(self.db, name)
        if existing:
            return False
        await category_repo.create(self.db, {"name": name, "description": description})
        return True

    async def update(
        self, category_id: int, name: str | None, description: str | None
    ) -> bool:
        obj = await category_repo.get(self.db, category_id)
        if not obj or obj.deleted == 1:
            return False
        updates: dict = {}
        if name is not None:
            updates["name"] = name
        if description is not None:
            updates["description"] = description
        if updates:
            await category_repo.update(self.db, category_id, updates)
        return True

    async def delete(self, category_id: int) -> bool:
        return await category_repo.hard_delete(self.db, category_id)
