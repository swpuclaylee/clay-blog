from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.schemas.base import ResponseModel
from src.services.article import ArticleService

router = APIRouter(prefix="/archive", tags=["归档"])


@router.get("/list")
async def get_archive_list(db: AsyncSession = Depends(get_db)):
    """获取归档列表（全量，按 createTime 降序）"""
    service = ArticleService(db)
    data = await service.get_archive_list()
    return ResponseModel(data=data)
