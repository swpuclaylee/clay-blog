from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.client import Client
from src.repositories.base import BaseRepository


class ClientRepository(BaseRepository[Client]):
    def __init__(self):
        super().__init__(Client)

    async def get_page(
        self, db: AsyncSession, page: int, size: int
    ) -> tuple[list[Client], int]:
        total = (
            await db.execute(select(func.count()).select_from(Client))
        ).scalar() or 0
        items = (
            (await db.execute(select(Client).offset((page - 1) * size).limit(size)))
            .scalars()
            .all()
        )
        return list(items), total


client_repo = ClientRepository()
