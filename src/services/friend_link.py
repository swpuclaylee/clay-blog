from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.friend_link import friend_link_repo
from src.schemas.common import PageResult
from src.schemas.friend_link import FriendLinkItem


class FriendLinkService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(self) -> list[FriendLinkItem]:
        items = await friend_link_repo.get_all(self.db)
        return [
            FriendLinkItem(
                id=i.id,
                name=i.name,
                url=i.url,
                avatar=i.avatar,
                description=i.description,
            )
            for i in items
        ]

    async def get_page(self, page: int, size: int) -> PageResult[FriendLinkItem]:
        items, total = await friend_link_repo.get_page(self.db, page, size)
        pages = (total + size - 1) // size
        result = [
            FriendLinkItem(
                id=i.id,
                name=i.name,
                url=i.url,
                avatar=i.avatar,
                description=i.description,
            )
            for i in items
        ]
        return PageResult(items=result, total=total, page=page, size=size, pages=pages)

    async def create(self, data: dict) -> None:
        await friend_link_repo.create(self.db, data)

    async def update(self, link_id: int, data: dict) -> bool:
        obj = await friend_link_repo.get(self.db, link_id)
        if not obj:
            return False
        await friend_link_repo.update(
            self.db, link_id, {k: v for k, v in data.items() if v is not None}
        )
        return True

    async def delete(self, link_id: int) -> bool:
        return await friend_link_repo.hard_delete(self.db, link_id)
