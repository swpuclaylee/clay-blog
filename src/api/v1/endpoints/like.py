from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.schemas.base import ResponseModel
from src.services.like import LikeService

router = APIRouter(prefix="/like", tags=["点赞"])


class LikeRequest(BaseModel):
    articleId: int


@router.get("/check/{article_id}")
async def check_like(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = LikeService(db)
    liked = await service.is_liked(current_user.id, article_id)
    return ResponseModel(data=liked)


@router.post("", response_model=ResponseModel[None])
async def like_article(
    body: LikeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = LikeService(db)
    await service.like(current_user.id, body.articleId)
    return ResponseModel(message="点赞成功")


@router.delete("/{article_id}", response_model=ResponseModel[None])
async def unlike_article(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = LikeService(db)
    await service.unlike(current_user.id, article_id)
    return ResponseModel(message="取消成功")
