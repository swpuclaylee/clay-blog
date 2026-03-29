from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.article import Article, ArticleTag
from src.repositories.base import BaseRepository


class ArticleRepository(BaseRepository[Article]):
    def __init__(self):
        super().__init__(Article)

    async def get_published_page(
        self,
        db: AsyncSession,
        page: int,
        size: int,
        sort: str = "create_time",
        category_id: int | None = None,
        tag_id: int | None = None,
        keyword: str | None = None,
    ) -> tuple[list[Article], int]:
        query = select(Article).where(Article.deleted == 0, Article.status == 1)
        count_q = (
            select(func.count())
            .select_from(Article)
            .where(Article.deleted == 0, Article.status == 1)
        )

        if category_id:
            query = query.where(Article.category_id == category_id)
            count_q = count_q.where(Article.category_id == category_id)
        if keyword:
            like = f"%{keyword}%"
            query = query.where(Article.title.ilike(like))
            count_q = count_q.where(Article.title.ilike(like))
        if tag_id:
            tag_article_ids = select(ArticleTag.article_id).where(
                ArticleTag.tag_id == tag_id
            )
            query = query.where(Article.id.in_(tag_article_ids))
            count_q = count_q.where(Article.id.in_(tag_article_ids))

        if sort == "view":
            query = query.order_by(Article.view_count.desc())
        else:
            query = query.order_by(Article.create_time.desc())

        total = (await db.execute(count_q)).scalar() or 0
        items = (
            (await db.execute(query.offset((page - 1) * size).limit(size)))
            .scalars()
            .all()
        )
        return list(items), total

    async def get_admin_page(
        self,
        db: AsyncSession,
        page: int,
        size: int,
        keyword: str | None = None,
        status: int | None = None,
        category_id: int | None = None,
    ) -> tuple[list[Article], int]:
        query = select(Article).where(Article.deleted == 0)
        count_q = select(func.count()).select_from(Article).where(Article.deleted == 0)

        if keyword:
            like = f"%{keyword}%"
            query = query.where(Article.title.ilike(like))
            count_q = count_q.where(Article.title.ilike(like))
        if status is not None:
            query = query.where(Article.status == status)
            count_q = count_q.where(Article.status == status)
        if category_id:
            query = query.where(Article.category_id == category_id)
            count_q = count_q.where(Article.category_id == category_id)

        query = query.order_by(Article.create_time.desc())
        total = (await db.execute(count_q)).scalar() or 0
        items = (
            (await db.execute(query.offset((page - 1) * size).limit(size)))
            .scalars()
            .all()
        )
        return list(items), total

    async def get_related(
        self, db: AsyncSession, article_id: int, category_id: int | None, limit: int = 5
    ) -> list[Article]:
        query = select(Article).where(
            Article.id != article_id,
            Article.deleted == 0,
            Article.status == 1,
        )
        if category_id:
            query = query.where(Article.category_id == category_id)
        query = query.order_by(Article.create_time.desc()).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_archive_list(self, db: AsyncSession) -> list[Article]:
        result = await db.execute(
            select(Article)
            .where(Article.deleted == 0, Article.status == 1)
            .order_by(Article.create_time.desc())
        )
        return list(result.scalars().all())

    # ---- ArticleTag helpers ----

    async def get_tag_ids(self, db: AsyncSession, article_id: int) -> list[int]:
        result = await db.execute(
            select(ArticleTag.tag_id).where(ArticleTag.article_id == article_id)
        )
        return list(result.scalars().all())

    async def set_tags(self, db: AsyncSession, article_id: int, tag_ids: list[int]):
        await db.execute(delete(ArticleTag).where(ArticleTag.article_id == article_id))
        for tag_id in tag_ids:
            db.add(ArticleTag(article_id=article_id, tag_id=tag_id))
        await db.commit()

    async def total_views(self, db: AsyncSession) -> int:
        result = await db.execute(
            select(func.sum(Article.view_count)).where(Article.deleted == 0)
        )
        return result.scalar() or 0


article_repo = ArticleRepository()
