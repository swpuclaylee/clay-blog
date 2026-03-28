from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db, require_admin
from src.models.user import User
from src.schemas.base import ResponseModel
from src.schemas.message import MessageCreate, MessageReply
from src.services.message import MessageService

router = APIRouter(prefix="/message", tags=["留言"])


@router.get("/page")
async def get_page(
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_db),
):
    service = MessageService(db)
    return ResponseModel(data=await service.get_page(page, size))


@router.post("", response_model=ResponseModel[None])
async def create_message(
    body: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MessageService(db)
    await service.create(current_user.id, body.content)
    return ResponseModel(message="留言成功")


@router.post("/reply", response_model=ResponseModel[None])
async def reply_message(
    body: MessageReply,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = MessageService(db)
    ok = await service.reply(admin.id, body.messageId, body.content)
    if not ok:
        return ResponseModel(code=0, message="留言不存在")
    return ResponseModel(message="回复成功")


@router.delete("/{message_id}", response_model=ResponseModel[None])
async def delete_message(
    message_id: int,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = MessageService(db)
    ok = await service.delete(message_id)
    if not ok:
        return ResponseModel(code=0, message="留言不存在")
    return ResponseModel(message="删除成功")
