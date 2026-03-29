from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.tag import tag_repo
from src.schemas.common import PageResult
from src.schemas.tag import TagItem


class TagService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(self) -> list[TagItem]:
        items = await tag_repo.get_all(self.db)
        result = []
        for t in items:
            count = await tag_repo.article_count(self.db, t.id)
            result.append(TagItem(id=t.id, name=t.name, articleCount=count))
        return result

    async def get_page(self, page: int, size: int) -> PageResult[TagItem]:
        items, total = await tag_repo.get_page(self.db, page, size)
        pages = (total + size - 1) // size
        result = []
        for t in items:
            count = await tag_repo.article_count(self.db, t.id)
            result.append(TagItem(id=t.id, name=t.name, articleCount=count))
        return PageResult(items=result, total=total, page=page, size=size, pages=pages)

    async def create(self, name: str) -> bool:
        existing = await tag_repo.get_by_name(self.db, name)
        if existing:
            return False
        await tag_repo.create(self.db, {"name": name})
        return True

    async def update(self, tag_id: int, name: str) -> bool:
        obj = await tag_repo.get(self.db, tag_id)
        if not obj:
            return False
        await tag_repo.update(self.db, tag_id, {"name": name})
        return True

    async def delete(self, tag_id: int) -> bool:
        return await tag_repo.hard_delete(self.db, tag_id)
