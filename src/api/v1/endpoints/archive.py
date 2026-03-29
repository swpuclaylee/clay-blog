from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.schemas.base import ResponseModel
from src.services.article import ArticleService

router = APIRouter(prefix="/archive", tags=["归档"])


@router.get("/list", summary="获取文章归档列表（全量，按发布时间降序）")
async def get_archive_list(db: AsyncSession = Depends(get_db)):
    service = ArticleService(db)
    data = await service.get_archive_list()
    return ResponseModel(data=data)
