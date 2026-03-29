from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, require_admin
from src.models.user import User
from src.schemas.base import ResponseModel
from src.schemas.friend_link import FriendLinkCreate, FriendLinkUpdate
from src.services.friend_link import FriendLinkService

router = APIRouter(prefix="/friend-link", tags=["友链"])


@router.get("/list", summary="获取全部友链（前台）")
async def get_list(db: AsyncSession = Depends(get_db)):
    service = FriendLinkService(db)
    return ResponseModel(data=await service.get_list())


@router.get("/page", summary="分页查询友链（管理员）")
async def get_page(
    page: int = 1,
    size: int = 20,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = FriendLinkService(db)
    return ResponseModel(data=await service.get_page(page, size))


@router.post("", response_model=ResponseModel[None], summary="新增友链（管理员）")
async def create(
    body: FriendLinkCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = FriendLinkService(db)
    await service.create(body.model_dump())
    return ResponseModel(message="操作成功")


@router.put("/{link_id}", response_model=ResponseModel[None], summary="更新友链（管理员）")
async def update(
    link_id: int,
    body: FriendLinkUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = FriendLinkService(db)
    ok = await service.update(link_id, body.model_dump())
    if not ok:
        return ResponseModel(code=0, message="友链不存在")
    return ResponseModel(message="操作成功")


@router.delete("/{link_id}", response_model=ResponseModel[None], summary="删除友链（管理员）")
async def delete(
    link_id: int,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = FriendLinkService(db)
    ok = await service.delete(link_id)
    if not ok:
        return ResponseModel(code=0, message="友链不存在")
    return ResponseModel(message="操作成功")
