from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, require_admin
from src.models.article import Article
from src.models.comment import Comment
from src.models.user import User
from src.repositories.article import article_repo
from src.schemas.base import ResponseModel
from src.schemas.dashboard import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get(
    "/stats", response_model=ResponseModel[DashboardStats], summary="获取博客统计数据（管理员）"
)
async def get_stats(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    article_count = (
        await db.execute(
            select(func.count()).select_from(Article).where(Article.deleted == 0)
        )
    ).scalar() or 0

    comment_count = (
        await db.execute(
            select(func.count()).select_from(Comment).where(Comment.deleted == 0)
        )
    ).scalar() or 0

    user_count = (
        await db.execute(select(func.count()).select_from(User))
    ).scalar() or 0

    total_views = await article_repo.total_views(db)

    return ResponseModel(
        data=DashboardStats(
            articleCount=article_count,
            commentCount=comment_count,
            userCount=user_count,
            totalViews=total_views,
        )
    )
