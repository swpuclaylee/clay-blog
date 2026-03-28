from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, require_admin
from src.models.user import User
from src.schemas.article import (
    ArticleCreate,
    ArticleIdResponse,
    ArticleStatusUpdate,
    ArticleUpdate,
    RecommendCreate,
)
from src.schemas.base import ResponseModel
from src.services.article import ArticleService

router = APIRouter(prefix="/article", tags=["文章"])


@router.get("/published/page")
async def get_published_page(
    page: int = 1,
    size: int = 10,
    sort: str = "create_time",
    categoryId: int | None = None,
    tagId: int | None = None,
    keyword: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """前台：分页获取已发布文章"""
    service = ArticleService(db)
    result = await service.get_published_page(
        page, size, sort, categoryId, tagId, keyword
    )
    return ResponseModel(data=result)


@router.get("/recommend")
async def get_recommend(db: AsyncSession = Depends(get_db)):
    """前台：推荐文章列表"""
    service = ArticleService(db)
    data = await service.get_recommend_list()
    return ResponseModel(data=data)


@router.get("/page")
async def get_admin_page(
    page: int = 1,
    size: int = 10,
    keyword: str | None = None,
    status: int | None = None,
    categoryId: int | None = None,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """后台：分页查询所有文章"""
    service = ArticleService(db)
    result = await service.get_admin_page(page, size, keyword, status, categoryId)
    return ResponseModel(data=result)


@router.get("/{article_id}/related")
async def get_related(article_id: int, db: AsyncSession = Depends(get_db)):
    """前台：相关推荐文章"""
    service = ArticleService(db)
    data = await service.get_related(article_id)
    return ResponseModel(data=data)


@router.get("/{article_id}")
async def get_detail(article_id: int, db: AsyncSession = Depends(get_db)):
    """前台：文章详情（浏览量+1）"""
    service = ArticleService(db)
    data = await service.get_detail(article_id)
    if not data:
        return ResponseModel(code=0, message="文章不存在")
    return ResponseModel(data=data)


@router.post("", response_model=ResponseModel[ArticleIdResponse])
async def create_article(
    body: ArticleCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """后台：新增文章"""
    service = ArticleService(db)
    data = body.model_dump()
    result = await service.create(admin.id, data)
    return ResponseModel(data=result)


@router.put("/recommend", response_model=ResponseModel[None])
async def add_recommend(
    body: RecommendCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """后台：添加推荐文章"""
    service = ArticleService(db)
    ok = await service.add_recommend(body.articleId)
    if not ok:
        return ResponseModel(code=0, message="文章不存在")
    return ResponseModel(message="操作成功")


@router.delete("/recommend/{article_id}", response_model=ResponseModel[None])
async def remove_recommend(
    article_id: int,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """后台：删除推荐文章"""
    service = ArticleService(db)
    await service.remove_recommend(article_id)
    return ResponseModel(message="操作成功")


@router.put("/{article_id}/status", response_model=ResponseModel[None])
async def update_status(
    article_id: int,
    body: ArticleStatusUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """后台：切换文章状态"""
    service = ArticleService(db)
    ok = await service.update_status(article_id, body.status)
    if not ok:
        return ResponseModel(code=0, message="文章不存在")
    return ResponseModel(message="操作成功")


@router.put("/{article_id}", response_model=ResponseModel[None])
async def update_article(
    article_id: int,
    body: ArticleUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """后台：更新文章"""
    service = ArticleService(db)
    ok = await service.update(article_id, body.model_dump(exclude_none=True))
    if not ok:
        return ResponseModel(code=0, message="文章不存在")
    return ResponseModel(message="更新成功")


@router.delete("/{article_id}", response_model=ResponseModel[None])
async def delete_article(
    article_id: int,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """后台：删除文章"""
    service = ArticleService(db)
    ok = await service.delete(article_id)
    if not ok:
        return ResponseModel(code=0, message="文章不存在")
    return ResponseModel(message="删除成功")
