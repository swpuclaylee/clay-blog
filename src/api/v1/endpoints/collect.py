from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db, require_admin
from src.models.user import User
from src.schemas.base import ResponseModel
from src.services.collect import CollectService

router = APIRouter(prefix="/collect", tags=["收藏"])


class CollectRequest(BaseModel):
    articleId: int


@router.get("/check/{article_id}", summary="检查是否已收藏")
async def check_collect(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CollectService(db)
    return ResponseModel(data=await service.is_collected(current_user.id, article_id))


@router.post("", response_model=ResponseModel[None], summary="收藏文章")
async def collect(
    body: CollectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CollectService(db)
    await service.collect(current_user.id, body.articleId)
    return ResponseModel(message="收藏成功")


@router.delete("/{article_id}", response_model=ResponseModel[None], summary="取消收藏")
async def uncollect(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CollectService(db)
    await service.uncollect(current_user.id, article_id)
    return ResponseModel(message="取消收藏")


@router.get("/page", summary="我的收藏列表（分页）")
async def get_my_page(
    page: int = 1,
    size: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CollectService(db)
    return ResponseModel(data=await service.get_page(current_user.id, page, size))


@router.get("/admin/page", summary="后台：收藏列表（管理员）")
async def get_admin_page(
    page: int = 1,
    size: int = 20,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = CollectService(db)
    return ResponseModel(data=await service.get_admin_page(page, size))
