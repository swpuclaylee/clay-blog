from datetime import datetime

from sqlalchemy import DateTime, Integer, SmallInteger, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Comment(Base):
    """文章评论表"""

    __tablename__ = "comment"

    article_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="文章ID")
    from_user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="评论者ID")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="评论内容")
    comment_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="评论时间",
    )
    deleted: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, comment="是否删除：1是 0否"
    )


class Reply(Base):
    """评论回复表"""

    __tablename__ = "reply"

    article_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="文章ID")
    comment_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="所属评论ID")
    from_user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="回复者ID")
    to_user_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="被回复者ID"
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="回复内容")
    reply_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="回复时间",
    )
    deleted: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, comment="是否删除：1是 0否"
    )
