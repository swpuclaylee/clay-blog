from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.message import message_repo
from src.repositories.user import user_repo
from src.schemas.common import PageResult
from src.schemas.message import MessageItem, MessageReplyItem, UserBrief


async def _user_brief(db, user_id: int) -> UserBrief:
    u = await user_repo.get(db, user_id)
    if u:
        return UserBrief(id=u.id, nickname=u.nickname, avatar=u.avatar)
    return UserBrief(id=user_id, nickname=None, avatar=None)


class MessageService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_page(self, page: int, size: int) -> PageResult[MessageItem]:
        messages, total = await message_repo.get_root_page(self.db, page, size)
        pages = (total + size - 1) // size
        items = []
        for m in messages:
            user = await _user_brief(self.db, m.from_user_id)
            replies_raw = await message_repo.get_replies(self.db, m.id)
            replies = []
            for r in replies_raw:
                ru = await _user_brief(self.db, r.from_user_id)
                replies.append(MessageReplyItem(id=r.id, content=r.content, user=ru))
            items.append(
                MessageItem(
                    id=m.id,
                    content=m.content,
                    createTime=m.create_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    user=user,
                    replies=replies,
                )
            )
        return PageResult(items=items, total=total, page=page, size=size, pages=pages)

    async def create(self, user_id: int, content: str) -> None:
        await message_repo.create(
            self.db, {"from_user_id": user_id, "content": content}
        )

    async def reply(self, admin_id: int, message_id: int, content: str) -> bool:
        parent = await message_repo.get(self.db, message_id)
        if not parent:
            return False
        await message_repo.create(
            self.db,
            {
                "pid": message_id,
                "from_user_id": admin_id,
                "to_user_id": parent.from_user_id,
                "content": content,
            },
        )
        return True

    async def delete(self, message_id: int) -> bool:
        return await message_repo.hard_delete(self.db, message_id)
