from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.article import article_repo
from src.repositories.category import category_repo
from src.repositories.tag import tag_repo
from src.repositories.user import user_repo
from src.schemas.article import (
    ArticleAdminItem,
    ArticleDetail,
    ArticleIdResponse,
    ArticleListItem,
    ArticleRelatedItem,
    AuthorBrief,
    CategoryBrief,
    RecommendItem,
    TagBrief,
)
from src.schemas.common import PageResult


async def _build_category(db, category_id: int | None) -> CategoryBrief | None:
    if not category_id:
        return None
    cat = await category_repo.get(db, category_id)
    if cat:
        return CategoryBrief(id=cat.id, name=cat.name)
    return None


async def _build_tags(db, article_id: int) -> list[TagBrief]:
    tag_ids = await article_repo.get_tag_ids(db, article_id)
    tags = await tag_repo.get_by_ids(db, tag_ids)
    return [TagBrief(id=t.id, name=t.name) for t in tags]


def _fmt_dt(dt: datetime | None) -> str:
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


class ArticleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_published_page(
        self,
        page: int,
        size: int,
        sort: str = "create_time",
        category_id: int | None = None,
        tag_id: int | None = None,
        keyword: str | None = None,
    ) -> PageResult[ArticleListItem]:
        items, total = await article_repo.get_published_page(
            self.db, page, size, sort, category_id, tag_id, keyword
        )
        pages = (total + size - 1) // size
        result = []
        for a in items:
            result.append(
                ArticleListItem(
                    id=a.id,
                    title=a.title,
                    summary=a.summary,
                    cover=a.cover,
                    category=await _build_category(self.db, a.category_id),
                    tags=await _build_tags(self.db, a.id),
                    viewCount=a.view_count,
                    likeCount=a.like_count,
                    collectCount=a.collect_count,
                    commentCount=a.comment_count,
                    createTime=_fmt_dt(a.create_time),
                )
            )
        return PageResult(items=result, total=total, page=page, size=size, pages=pages)

    async def get_detail(self, article_id: int) -> ArticleDetail | None:
        a = await article_repo.get(self.db, article_id)
        if not a or a.deleted == 1:
            return None
        # 增加浏览量
        await article_repo.update(self.db, article_id, {"view_count": a.view_count + 1})

        author_obj = await user_repo.get(self.db, a.user_id)
        author = AuthorBrief(
            id=author_obj.id if author_obj else a.user_id,
            nickname=author_obj.nickname if author_obj else None,
            avatar=author_obj.avatar if author_obj else None,
        )
        return ArticleDetail(
            id=a.id,
            title=a.title,
            content=a.content,
            summary=a.summary,
            cover=a.cover,
            status=a.status,
            viewCount=a.view_count + 1,
            likeCount=a.like_count,
            collectCount=a.collect_count,
            commentCount=a.comment_count,
            category=await _build_category(self.db, a.category_id),
            tags=await _build_tags(self.db, a.id),
            author=author,
            createTime=_fmt_dt(a.create_time),
            updateTime=_fmt_dt(a.update_time),
        )

    async def get_related(self, article_id: int) -> list[ArticleRelatedItem]:
        a = await article_repo.get(self.db, article_id)
        if not a:
            return []
        related = await article_repo.get_related(self.db, article_id, a.category_id)
        return [
            ArticleRelatedItem(
                id=r.id, title=r.title, cover=r.cover, createTime=_fmt_dt(r.create_time)
            )
            for r in related
        ]

    async def get_recommend_list(self) -> list[RecommendItem]:
        items = await article_repo.get_recommend_list(self.db)
        return [RecommendItem(id=a.id, title=a.title) for a in items]

    async def get_admin_page(
        self,
        page: int,
        size: int,
        keyword: str | None = None,
        status: int | None = None,
        category_id: int | None = None,
    ) -> PageResult[ArticleAdminItem]:
        items, total = await article_repo.get_admin_page(
            self.db, page, size, keyword, status, category_id
        )
        pages = (total + size - 1) // size
        result = []
        for a in items:
            result.append(
                ArticleAdminItem(
                    id=a.id,
                    title=a.title,
                    category=await _build_category(self.db, a.category_id),
                    status=a.status,
                    viewCount=a.view_count,
                    createTime=_fmt_dt(a.create_time),
                )
            )
        return PageResult(items=result, total=total, page=page, size=size, pages=pages)

    async def create(self, user_id: int, data: dict) -> ArticleIdResponse:
        tag_ids = data.pop("tagIds", [])
        category_id = data.pop("categoryId", None)

        # 补充分类名冗余
        category_name = None
        if category_id:
            cat = await category_repo.get(self.db, category_id)
            if cat:
                category_name = cat.name

        # 自动截取摘要
        content = data.get("content", "") or ""
        if not data.get("summary") and content:
            data["summary"] = content[:200].replace("\n", " ")

        data.update(
            {
                "user_id": user_id,
                "category_id": category_id,
                "category_name": category_name,
            }
        )
        if data.get("status") == 1:
            data["publish_time"] = datetime.now(timezone.utc)

        article = await article_repo.create(self.db, data)
        await article_repo.set_tags(self.db, article.id, tag_ids)
        return ArticleIdResponse(id=article.id)

    async def update(self, article_id: int, data: dict) -> bool:
        tag_ids = data.pop("tagIds", None)
        category_id = data.pop("categoryId", None)

        obj = await article_repo.get(self.db, article_id)
        if not obj or obj.deleted == 1:
            return False

        if category_id is not None:
            data["category_id"] = category_id
            cat = await category_repo.get(self.db, category_id)
            if cat:
                data["category_name"] = cat.name

        if data.get("status") == 1 and obj.status != 1:
            data["publish_time"] = datetime.now(timezone.utc)

        await article_repo.update(self.db, article_id, data)
        if tag_ids is not None:
            await article_repo.set_tags(self.db, article_id, tag_ids)
        return True

    async def delete(self, article_id: int) -> bool:
        return await article_repo.soft_delete(self.db, article_id)

    async def update_status(self, article_id: int, status: int) -> bool:
        obj = await article_repo.get(self.db, article_id)
        if not obj or obj.deleted == 1:
            return False
        updates: dict = {"status": status}
        if status == 1 and obj.status != 1:
            updates["publish_time"] = datetime.now(timezone.utc)
        await article_repo.update(self.db, article_id, updates)
        return True

    async def add_recommend(self, article_id: int) -> bool:
        obj = await article_repo.get(self.db, article_id)
        if not obj or obj.deleted == 1:
            return False
        await article_repo.update(self.db, article_id, {"is_recommend": 1})
        return True

    async def remove_recommend(self, article_id: int) -> bool:
        obj = await article_repo.get(self.db, article_id)
        if not obj:
            return False
        await article_repo.update(self.db, article_id, {"is_recommend": 0})
        return True

    async def get_archive_list(self) -> list[dict]:
        items = await article_repo.get_archive_list(self.db)
        return [
            {"id": a.id, "title": a.title, "createTime": _fmt_dt(a.create_time)}
            for a in items
        ]

    async def total_views(self) -> int:
        return await article_repo.total_views(self.db)
