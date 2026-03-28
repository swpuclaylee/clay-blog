from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, require_admin
from src.models.user import User
from src.schemas.base import ResponseModel
from src.schemas.category import CategoryCreate, CategoryUpdate
from src.services.category import CategoryService

router = APIRouter(prefix="/category", tags=["分类"])


@router.get("/list")
async def get_list(db: AsyncSession = Depends(get_db)):
    service = CategoryService(db)
    return ResponseModel(data=await service.get_list())


@router.get("/page")
async def get_page(
    page: int = 1,
    size: int = 20,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)
    return ResponseModel(data=await service.get_page(page, size))


@router.post("", response_model=ResponseModel[None])
async def create(
    body: CategoryCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)
    ok = await service.create(body.name, body.description)
    if not ok:
        return ResponseModel(code=0, message="分类名已存在")
    return ResponseModel(message="操作成功")


@router.put("/{category_id}", response_model=ResponseModel[None])
async def update(
    category_id: int,
    body: CategoryUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)
    ok = await service.update(category_id, body.name, body.description)
    if not ok:
        return ResponseModel(code=0, message="分类不存在")
    return ResponseModel(message="操作成功")


@router.delete("/{category_id}", response_model=ResponseModel[None])
async def delete(
    category_id: int,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)
    ok = await service.delete(category_id)
    if not ok:
        return ResponseModel(code=0, message="分类不存在")
    return ResponseModel(message="操作成功")
