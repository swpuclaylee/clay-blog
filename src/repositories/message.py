from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.message import Message
from src.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    def __init__(self):
        super().__init__(Message)

    async def get_root_page(
        self, db: AsyncSession, page: int, size: int
    ) -> tuple[list[Message], int]:
        """获取顶级留言（pid is null）"""
        query = (
            select(Message)
            .where(Message.pid.is_(None), Message.deleted == 0)
            .order_by(Message.create_time.desc())
        )
        count_q = (
            select(func.count())
            .select_from(Message)
            .where(Message.pid.is_(None), Message.deleted == 0)
        )
        total = (await db.execute(count_q)).scalar() or 0
        items = (
            (await db.execute(query.offset((page - 1) * size).limit(size)))
            .scalars()
            .all()
        )
        return list(items), total

    async def get_replies(self, db: AsyncSession, pid: int) -> list[Message]:
        result = await db.execute(
            select(Message)
            .where(Message.pid == pid, Message.deleted == 0)
            .order_by(Message.create_time.asc())
        )
        return list(result.scalars().all())

    async def soft_delete(self, db: AsyncSession, id: int) -> bool:
        obj = await self.get(db, id)
        if not obj:
            return False
        obj.deleted = 1
        await db.commit()
        return True


message_repo = MessageRepository()
