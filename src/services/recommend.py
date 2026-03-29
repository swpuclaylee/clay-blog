"""
推荐文章服务 —— 基于 Redis sorted set

key:   recommend
member: str(article_id)
score:  推荐分值（越高越靠前）

操作：
  save(article_id, score)  -> zadd recommend {article_id: score}  覆盖已有分值
  delete(article_id)       -> zrem recommend article_id
  list()                   -> zrevrange recommend 0 -1 withscores，关联查文章标题
"""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache.redis_ops import redis_cache
from src.repositories.article import article_repo

_RECOMMEND_KEY = "recommend"


class RecommendService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, article_id: int, score: float) -> None:
        """添加或更新推荐分值（zadd 自动覆盖）"""
        await redis_cache.zadd(_RECOMMEND_KEY, {str(article_id): score})
        logger.info(f"文章 {article_id} 已保存到推荐，分值={score}")

    async def delete(self, article_id: int) -> None:
        """从推荐列表移除"""
        await redis_cache.zrem(_RECOMMEND_KEY, str(article_id))
        logger.info(f"文章 {article_id} 已从推荐移除")

    async def list(self) -> list[dict]:
        """
        按分值降序返回推荐列表，关联查询文章标题。
        已删除的文章自动过滤，不从 Redis 中清理（下次覆盖时自动失效）。
        """
        raw: list[tuple[bytes | str, float]] = await redis_cache.zrevrange(
            _RECOMMEND_KEY, 0, -1, withscores=True
        )
        result = []
        for member, score in raw:
            article_id = int(member)
            article = await article_repo.get(self.db, article_id)
            if not article:
                continue
            result.append(
                {
                    "id": str(article_id),
                    "title": article.title,
                    "score": score,
                }
            )
        return result
