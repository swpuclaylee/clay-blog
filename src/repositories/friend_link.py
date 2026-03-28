from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.friend_link import FriendLink
from src.repositories.base import BaseRepository


class FriendLinkRepository(BaseRepository[FriendLink]):
    def __init__(self):
        super().__init__(FriendLink)

    async def get_all(self, db: AsyncSession) -> list[FriendLink]:
        result = await db.execute(select(FriendLink))
        return list(result.scalars().all())

    async def get_page(
        self, db: AsyncSession, page: int, size: int
    ) -> tuple[list[FriendLink], int]:
        total = (
            await db.execute(select(func.count()).select_from(FriendLink))
        ).scalar() or 0
        items = (
            (await db.execute(select(FriendLink).offset((page - 1) * size).limit(size)))
            .scalars()
            .all()
        )
        return list(items), total


friend_link_repo = FriendLinkRepository()
