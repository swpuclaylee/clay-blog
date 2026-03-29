from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, require_admin
from src.models.user import User
from src.schemas.article import (
    ArticleCreate,
    ArticleIdResponse,
    ArticleStatusUpdate,
    ArticleUpdate,
)
from src.schemas.base import ResponseModel
from src.services.article import ArticleService
from src.services.recommend import RecommendService

router = APIRouter(prefix="/article", tags=["文章"])


@router.get("/published/page", summary="前台：分页获取已发布文章")
async def get_published_page(
    page: int = 1,
    size: int = 10,
    sort: str = "create_time",
    categoryId: int | None = None,
    tagId: int | None = None,
    keyword: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    result = await service.get_published_page(
        page, size, sort, categoryId, tagId, keyword
    )
    return ResponseModel(data=result)


@router.get("/recommend/list", summary="获取推荐文章列表（Redis sorted set，按分值降序）")
async def get_recommend_list(db: AsyncSession = Depends(get_db)):
    service = RecommendService(db)
    return ResponseModel(data=await service.list())


@router.post("/recommend/save", summary="保存/更新推荐文章（管理员）")
async def save_recommend(
    articleId: int = Query(..., description="文章 ID"),
    score: float = Query(..., description="推荐分值，越高越靠前"),
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = RecommendService(db)
    await service.save(articleId, score)
    return ResponseModel(message="操作成功")


@router.delete("/recommend/delete/{article_id}", summary="取消推荐文章（管理员）")
async def delete_recommend(
    article_id: int,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = RecommendService(db)
    await service.delete(article_id)
    return ResponseModel(message="操作成功")


@router.get("/page", summary="后台：分页查询所有文章（管理员）")
async def get_admin_page(
    page: int = 1,
    size: int = 10,
    keyword: str | None = None,
    status: int | None = None,
    categoryId: int | None = None,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    result = await service.get_admin_page(page, size, keyword, status, categoryId)
    return ResponseModel(data=result)


@router.get("/{article_id}/related", summary="前台：获取相关文章推荐")
async def get_related(article_id: int, db: AsyncSession = Depends(get_db)):
    service = ArticleService(db)
    data = await service.get_related(article_id)
    return ResponseModel(data=data)


@router.get("/{article_id}", summary="前台：文章详情（浏览量 +1）")
async def get_detail(article_id: int, db: AsyncSession = Depends(get_db)):
    service = ArticleService(db)
    data = await service.get_detail(article_id)
    if not data:
        return ResponseModel(code=0, message="文章不存在")
    return ResponseModel(data=data)


@router.post(
    "", response_model=ResponseModel[ArticleIdResponse], summary="后台：新增文章（管理员）"
)
async def create_article(
    body: ArticleCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    result = await service.create(admin.id, body.model_dump())
    return ResponseModel(data=result)


@router.put(
    "/{article_id}/status", response_model=ResponseModel[None], summary="后台：切换文章状态（管理员）"
)
async def update_status(
    article_id: int,
    body: ArticleStatusUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    ok = await service.update_status(article_id, body.status)
    if not ok:
        return ResponseModel(code=0, message="文章不存在")
    return ResponseModel(message="操作成功")


@router.put("/{article_id}", response_model=ResponseModel[None], summary="后台：更新文章（管理员）")
async def update_article(
    article_id: int,
    body: ArticleUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    ok = await service.update(article_id, body.model_dump(exclude_none=True))
    if not ok:
        return ResponseModel(code=0, message="文章不存在")
    return ResponseModel(message="更新成功")


@router.delete(
    "/{article_id}", response_model=ResponseModel[None], summary="后台：删除文章（管理员）"
)
async def delete_article(
    article_id: int,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    ok = await service.delete(article_id)
    if not ok:
        return ResponseModel(code=0, message="文章不存在")
    return ResponseModel(message="删除成功")
