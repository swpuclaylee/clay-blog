from datetime import datetime

from sqlalchemy import DateTime, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Article(Base):
    """文章表"""

    __tablename__ = "article"

    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="作者ID")
    category_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="分类ID"
    )
    category_name: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="分类名（冗余）"
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False, comment="标题")
    summary: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="摘要"
    )
    content: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Markdown 内容"
    )
    html_content: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="富文本内容"
    )
    cover: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="封面图片"
    )
    original: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, comment="是否原创：1是 0否"
    )
    reproduce: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="转载地址"
    )
    # status: 0=草稿 1=已发布 2=回收站
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, comment="状态"
    )
    view_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="浏览量"
    )
    like_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="点赞数（冗余）"
    )
    collect_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="收藏数（冗余）"
    )
    comment_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="评论数（冗余）"
    )
    is_recommend: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, comment="是否推荐：1是 0否"
    )
    publish_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="发布时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )
    deleted: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, comment="是否删除：1是 0否"
    )


class ArticleTag(Base):
    """文章-标签关联表"""

    __tablename__ = "article_tag"

    article_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="文章ID")
    tag_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="标签ID")
