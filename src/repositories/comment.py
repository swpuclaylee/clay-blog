from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.comment import Comment, Reply
from src.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self):
        super().__init__(Comment)

    async def get_page_by_article(
        self, db: AsyncSession, article_id: int, page: int, size: int
    ) -> tuple[list[Comment], int]:
        query = (
            select(Comment)
            .where(Comment.article_id == article_id, Comment.deleted == 0)
            .order_by(Comment.comment_time.desc())
        )
        count_q = (
            select(func.count())
            .select_from(Comment)
            .where(Comment.article_id == article_id, Comment.deleted == 0)
        )
        total = (await db.execute(count_q)).scalar() or 0
        items = (
            (await db.execute(query.offset((page - 1) * size).limit(size)))
            .scalars()
            .all()
        )
        return list(items), total

    async def get_replies_by_comment(
        self, db: AsyncSession, comment_id: int
    ) -> list[Reply]:
        result = await db.execute(
            select(Reply)
            .where(Reply.comment_id == comment_id, Reply.deleted == 0)
            .order_by(Reply.reply_time.asc())
        )
        return list(result.scalars().all())

    async def get_admin_page(
        self, db: AsyncSession, page: int, size: int, keyword: str | None = None
    ) -> tuple[list[Comment], int]:
        query = select(Comment).where(Comment.deleted == 0)
        count_q = select(func.count()).select_from(Comment).where(Comment.deleted == 0)
        if keyword:
            like = f"%{keyword}%"
            query = query.where(Comment.content.ilike(like))
            count_q = count_q.where(Comment.content.ilike(like))
        query = query.order_by(Comment.comment_time.desc())
        total = (await db.execute(count_q)).scalar() or 0
        items = (
            (await db.execute(query.offset((page - 1) * size).limit(size)))
            .scalars()
            .all()
        )
        return list(items), total

    async def soft_delete(self, db: AsyncSession, id: int) -> bool:
        obj = await self.get(db, id)
        if not obj:
            return False
        obj.deleted = 1
        await db.commit()
        return True

    async def total_count(self, db: AsyncSession) -> int:
        result = await db.execute(
            select(func.count()).select_from(Comment).where(Comment.deleted == 0)
        )
        return result.scalar() or 0


class ReplyRepository(BaseRepository[Reply]):
    def __init__(self):
        super().__init__(Reply)

    async def soft_delete(self, db: AsyncSession, id: int) -> bool:
        obj = await self.get(db, id)
        if not obj:
            return False
        obj.deleted = 1
        await db.commit()
        return True


comment_repo = CommentRepository()
reply_repo = ReplyRepository()
