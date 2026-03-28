from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db, require_admin
from src.models.user import User
from src.schemas.base import ResponseModel
from src.schemas.comment import CommentCreate, ReplyCreate
from src.services.comment import CommentService

router = APIRouter(prefix="/comment", tags=["评论"])


@router.get("/page")
async def get_page(
    articleId: int,
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_db),
):
    service = CommentService(db)
    return ResponseModel(data=await service.get_page(articleId, page, size))


@router.post("", response_model=ResponseModel[None])
async def create_comment(
    body: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CommentService(db)
    await service.create(body.articleId, current_user.id, body.content)
    return ResponseModel(message="评论成功")


@router.post("/reply", response_model=ResponseModel[None])
async def create_reply(
    body: ReplyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CommentService(db)
    await service.create_reply(body.commentId, current_user.id, body.content)
    return ResponseModel(message="回复成功")


@router.delete("/reply/{reply_id}", response_model=ResponseModel[None])
async def delete_reply(
    reply_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CommentService(db)
    ok = await service.delete_reply(reply_id, current_user.id, current_user.admin == 1)
    if not ok:
        return ResponseModel(code=0, message="无权限或回复不存在")
    return ResponseModel(message="删除成功")


@router.get("/admin/page")
async def get_admin_page(
    page: int = 1,
    size: int = 20,
    keyword: str | None = None,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = CommentService(db)
    return ResponseModel(data=await service.get_admin_page(page, size, keyword))


@router.delete("/{comment_id}", response_model=ResponseModel[None])
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CommentService(db)
    ok = await service.delete_comment(
        comment_id, current_user.id, current_user.admin == 1
    )
    if not ok:
        return ResponseModel(code=0, message="无权限或评论不存在")
    return ResponseModel(message="删除成功")
