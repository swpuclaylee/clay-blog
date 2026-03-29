from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.article import article_repo
from src.repositories.comment import comment_repo, reply_repo
from src.repositories.user import user_repo
from src.schemas.comment import AdminCommentItem, CommentItem, ReplyItem, UserBrief
from src.schemas.common import PageResult


async def _user_brief(db, user_id: int) -> UserBrief:
    u = await user_repo.get(db, user_id)
    if u:
        return UserBrief(id=u.id, nickname=u.nickname, avatar=u.avatar)
    return UserBrief(id=user_id, nickname=None, avatar=None)


class CommentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_page(
        self, article_id: int, page: int, size: int
    ) -> PageResult[CommentItem]:
        comments, total = await comment_repo.get_page_by_article(
            self.db, article_id, page, size
        )
        pages = (total + size - 1) // size
        items = []
        for c in comments:
            user = await _user_brief(self.db, c.from_user_id)
            replies_raw = await comment_repo.get_replies_by_comment(self.db, c.id)
            replies = []
            for r in replies_raw:
                ru = await _user_brief(self.db, r.from_user_id)
                replies.append(
                    ReplyItem(
                        id=r.id,
                        content=r.content,
                        createTime=r.reply_time.strftime("%Y-%m-%dT%H:%M:%S"),
                        user=ru,
                    )
                )
            items.append(
                CommentItem(
                    id=c.id,
                    content=c.content,
                    createTime=c.comment_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    user=user,
                    replies=replies,
                )
            )
        return PageResult(items=items, total=total, page=page, size=size, pages=pages)

    async def create(self, article_id: int, user_id: int, content: str) -> None:
        await comment_repo.create(
            self.db,
            {
                "article_id": article_id,
                "from_user_id": user_id,
                "content": content,
            },
        )
        # 更新文章评论数冗余字段
        article = await article_repo.get(self.db, article_id)
        if article:
            await article_repo.update(
                self.db, article_id, {"comment_count": article.comment_count + 1}
            )

    async def create_reply(self, comment_id: int, user_id: int, content: str) -> None:
        comment = await comment_repo.get(self.db, comment_id)
        if not comment:
            return
        await reply_repo.create(
            self.db,
            {
                "article_id": comment.article_id,
                "comment_id": comment_id,
                "from_user_id": user_id,
                "content": content,
            },
        )

    async def delete_comment(
        self, comment_id: int, user_id: int, is_admin: bool
    ) -> bool:
        obj = await comment_repo.get(self.db, comment_id)
        if not obj:
            return False
        if not is_admin and obj.from_user_id != user_id:
            return False
        return await comment_repo.hard_delete(self.db, comment_id)

    async def delete_reply(self, reply_id: int, user_id: int, is_admin: bool) -> bool:
        obj = await reply_repo.get(self.db, reply_id)
        if not obj:
            return False
        if not is_admin and obj.from_user_id != user_id:
            return False
        return await reply_repo.hard_delete(self.db, reply_id)

    async def get_admin_page(
        self, page: int, size: int, keyword: str | None
    ) -> PageResult[AdminCommentItem]:
        comments, total = await comment_repo.get_admin_page(
            self.db, page, size, keyword
        )
        pages = (total + size - 1) // size
        items = []
        for c in comments:
            user = await _user_brief(self.db, c.from_user_id)
            article = await article_repo.get(self.db, c.article_id)
            items.append(
                AdminCommentItem(
                    id=c.id,
                    content=c.content,
                    createTime=c.comment_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    user=user,
                    article={"title": article.title if article else ""},
                )
            )
        return PageResult(items=items, total=total, page=page, size=size, pages=pages)

    async def total_count(self) -> int:
        return await comment_repo.total_count(self.db)
