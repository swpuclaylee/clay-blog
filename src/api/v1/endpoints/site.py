from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.models.article import Article
from src.models.category import Category
from src.models.tag import Tag
from src.repositories.user import user_repo
from src.schemas.base import ResponseModel
from src.schemas.site import SiteInfo

router = APIRouter(prefix="/site", tags=["站点"])


@router.get("/info", response_model=ResponseModel[SiteInfo], summary="获取站点信息（公开）")
async def get_site_info(db: AsyncSession = Depends(get_db)):
    admin = await user_repo.get_admin(db)

    article_count = (
        await db.execute(
            select(func.count())
            .select_from(Article)
            .where(Article.deleted == 0, Article.status == 1)
        )
    ).scalar() or 0

    category_count = (
        await db.execute(
            select(func.count())
            .select_from(Category)
            .where(Category.deleted == 0)
        )
    ).scalar() or 0

    tag_count = (
        await db.execute(select(func.count()).select_from(Tag))
    ).scalar() or 0

    return ResponseModel(
        data=SiteInfo(
            ownerName=admin.nickname if admin else None,
            ownerAvatar=admin.avatar if admin else None,
            ownerBio=admin.brief if admin else None,
            articleCount=article_count,
            categoryCount=category_count,
            tagCount=tag_count,
        )
    )
