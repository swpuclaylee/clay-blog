from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash, verify_password
from src.models.user import User
from src.repositories.user import user_repo
from src.schemas.common import PageResult
from src.schemas.user import UserListItem


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        return await user_repo.get(self.db, user_id)

    async def get_by_email(self, email: str) -> User | None:
        return await user_repo.get_by_email(self.db, email)

    async def register(
        self, email: str, password: str, username: str | None = None
    ) -> User:
        uname = username or email.split("@")[0]
        # 确保 username 唯一
        existing = await user_repo.get_by_username(self.db, uname)
        if existing:
            uname = f"{uname}_{email[:4]}"
        user = await user_repo.create(
            self.db,
            {
                "username": uname,
                "email": email,
                "password": get_password_hash(password),
                "nickname": uname,
            },
        )
        return user

    async def authenticate(self, email: str, password: str) -> User | None:
        user = await user_repo.get_by_email(self.db, email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    async def update_info(
        self, user: User, nickname: str | None, avatar: str | None, bio: str | None
    ) -> None:
        updates: dict = {}
        if nickname is not None:
            updates["nickname"] = nickname
        if avatar is not None:
            updates["avatar"] = avatar
        if bio is not None:
            updates["brief"] = bio
        if updates:
            await user_repo.update(self.db, user.id, updates)

    async def change_password(
        self, user: User, old_password: str, new_password: str
    ) -> bool:
        if not verify_password(old_password, user.password):
            return False
        await user_repo.update(
            self.db, user.id, {"password": get_password_hash(new_password)}
        )
        return True

    async def bind_email(self, user: User, email: str) -> bool:
        existing = await user_repo.get_by_email(self.db, email)
        if existing and existing.id != user.id:
            return False
        await user_repo.update(self.db, user.id, {"email": email})
        return True

    async def get_page(
        self, page: int, size: int, keyword: str | None
    ) -> PageResult[UserListItem]:
        items, total = await user_repo.get_page(self.db, page, size, keyword)
        pages = (total + size - 1) // size
        return PageResult(
            items=[UserListItem.from_orm(u) for u in items],
            total=total,
            page=page,
            size=size,
            pages=pages,
        )

    async def update_status(self, user_id: int, status: int) -> bool:
        if status not in (0, 1):
            return False
        obj = await user_repo.get(self.db, user_id)
        if not obj:
            return False
        await user_repo.update(self.db, user_id, {"status": status})
        return True
