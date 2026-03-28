import secrets

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.client import client_repo
from src.schemas.client import ClientItem
from src.schemas.common import PageResult


class ClientService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_page(self, page: int, size: int) -> PageResult[ClientItem]:
        items, total = await client_repo.get_page(self.db, page, size)
        pages = (total + size - 1) // size
        result = [ClientItem.from_orm(i) for i in items]
        return PageResult(items=result, total=total, page=page, size=size, pages=pages)

    async def create(self, name: str, description: str | None) -> None:
        await client_repo.create(
            self.db,
            {
                "name": name,
                "client_id": secrets.token_hex(16),
                "description": description,
            },
        )

    async def update(
        self, client_id: int, name: str | None, description: str | None
    ) -> bool:
        obj = await client_repo.get(self.db, client_id)
        if not obj:
            return False
        updates = {}
        if name is not None:
            updates["name"] = name
        if description is not None:
            updates["description"] = description
        if updates:
            await client_repo.update(self.db, client_id, updates)
        return True

    async def delete(self, client_id: int) -> bool:
        return await client_repo.hard_delete(self.db, client_id)
