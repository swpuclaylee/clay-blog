from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_page(
        self, db: AsyncSession, page: int, size: int, keyword: str | None = None
    ) -> tuple[list[User], int]:
        query = select(User)
        count_query = select(func.count()).select_from(User)
        if keyword:
            like = f"%{keyword}%"
            cond = or_(
                User.username.ilike(like),
                User.email.ilike(like),
                User.nickname.ilike(like),
            )
            query = query.where(cond)
            count_query = count_query.where(cond)

        total = (await db.execute(count_query)).scalar()
        items = (
            (await db.execute(query.offset((page - 1) * size).limit(size)))
            .scalars()
            .all()
        )
        return list(items), total


user_repo = UserRepository()
