from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.article import article_repo
from src.repositories.category import category_repo
from src.repositories.collect import collect_repo
from src.repositories.tag import tag_repo
from src.schemas.article import CategoryBrief, TagBrief
from src.schemas.common import PageResult


class CollectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def is_collected(self, user_id: int, article_id: int) -> bool:
        return (
            await collect_repo.get_by_user_article(self.db, user_id, article_id)
            is not None
        )

    async def collect(self, user_id: int, article_id: int) -> None:
        existing = await collect_repo.get_by_user_article(self.db, user_id, article_id)
        if existing:
            return
        await collect_repo.create(
            self.db, {"user_id": user_id, "article_id": article_id}
        )
        article = await article_repo.get(self.db, article_id)
        if article:
            await article_repo.update(
                self.db, article_id, {"collect_count": article.collect_count + 1}
            )

    async def uncollect(self, user_id: int, article_id: int) -> None:
        existing = await collect_repo.get_by_user_article(self.db, user_id, article_id)
        if not existing:
            return
        await collect_repo.hard_delete(self.db, existing.id)
        article = await article_repo.get(self.db, article_id)
        if article and article.collect_count > 0:
            await article_repo.update(
                self.db, article_id, {"collect_count": article.collect_count - 1}
            )

    async def get_page(self, user_id: int, page: int, size: int) -> PageResult[dict]:
        collects, total = await collect_repo.get_page_by_user(
            self.db, user_id, page, size
        )
        pages = (total + size - 1) // size
        items = []
        for col in collects:
            a = await article_repo.get(self.db, col.article_id)
            if not a:
                continue
            # 构建 category/tags
            category = None
            if a.category_id:
                cat = await category_repo.get(self.db, a.category_id)
                if cat:
                    category = CategoryBrief(id=cat.id, name=cat.name).model_dump()
            from src.repositories.article import article_repo as ar

            tag_ids = await ar.get_tag_ids(self.db, a.id)
            tags_objs = await tag_repo.get_by_ids(self.db, tag_ids)
            tags = [TagBrief(id=t.id, name=t.name).model_dump() for t in tags_objs]

            items.append(
                {
                    "id": col.id,
                    "createTime": col.create_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "article": {
                        "id": a.id,
                        "title": a.title,
                        "summary": a.summary,
                        "cover": a.cover,
                        "category": category,
                        "tags": tags,
                        "viewCount": a.view_count,
                        "likeCount": a.like_count,
                        "collectCount": a.collect_count,
                        "commentCount": a.comment_count,
                        "createTime": a.create_time.strftime("%Y-%m-%dT%H:%M:%S")
                        if a.create_time
                        else "",
                    },
                }
            )
        return PageResult(items=items, total=total, page=page, size=size, pages=pages)

    async def get_admin_page(self, page: int, size: int) -> PageResult[dict]:
        collects, total = await collect_repo.get_admin_page(self.db, page, size)
        pages = (total + size - 1) // size
        items = []
        for col in collects:
            from src.repositories.user import user_repo

            u = await user_repo.get(self.db, col.user_id)
            a = await article_repo.get(self.db, col.article_id)
            items.append(
                {
                    "id": col.id,
                    "createTime": col.create_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "user": {"nickname": u.nickname if u else None},
                    "article": {"title": a.title if a else ""},
                }
            )
        return PageResult(items=items, total=total, page=page, size=size, pages=pages)
