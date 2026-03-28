from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, require_admin
from src.models.user import User
from src.schemas.base import ResponseModel
from src.schemas.tag import TagCreate, TagUpdate
from src.services.tag import TagService

router = APIRouter(prefix="/tag", tags=["标签"])


@router.get("/list")
async def get_list(db: AsyncSession = Depends(get_db)):
    service = TagService(db)
    return ResponseModel(data=await service.get_list())


@router.get("/page")
async def get_page(
    page: int = 1,
    size: int = 20,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = TagService(db)
    return ResponseModel(data=await service.get_page(page, size))


@router.post("", response_model=ResponseModel[None])
async def create(
    body: TagCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = TagService(db)
    ok = await service.create(body.name)
    if not ok:
        return ResponseModel(code=0, message="标签名已存在")
    return ResponseModel(message="操作成功")


@router.put("/{tag_id}", response_model=ResponseModel[None])
async def update(
    tag_id: int,
    body: TagUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = TagService(db)
    ok = await service.update(tag_id, body.name)
    if not ok:
        return ResponseModel(code=0, message="标签不存在")
    return ResponseModel(message="操作成功")


@router.delete("/{tag_id}", response_model=ResponseModel[None])
async def delete(
    tag_id: int,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = TagService(db)
    ok = await service.delete(tag_id)
    if not ok:
        return ResponseModel(code=0, message="标签不存在")
    return ResponseModel(message="操作成功")
