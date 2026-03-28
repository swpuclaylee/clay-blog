from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, require_admin
from src.models.user import User
from src.schemas.base import ResponseModel
from src.schemas.client import ClientCreate, ClientUpdate
from src.services.client import ClientService

router = APIRouter(prefix="/client", tags=["客户端"])


@router.get("/page")
async def get_page(
    page: int = 1,
    size: int = 20,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ClientService(db)
    return ResponseModel(data=await service.get_page(page, size))


@router.post("", response_model=ResponseModel[None])
async def create(
    body: ClientCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ClientService(db)
    await service.create(body.name, body.description)
    return ResponseModel(message="操作成功")


@router.put("/{client_id}", response_model=ResponseModel[None])
async def update(
    client_id: int,
    body: ClientUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ClientService(db)
    ok = await service.update(client_id, body.name, body.description)
    if not ok:
        return ResponseModel(code=0, message="客户端不存在")
    return ResponseModel(message="操作成功")


@router.delete("/{client_id}", response_model=ResponseModel[None])
async def delete(
    client_id: int,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ClientService(db)
    ok = await service.delete(client_id)
    if not ok:
        return ResponseModel(code=0, message="客户端不存在")
    return ResponseModel(message="操作成功")
