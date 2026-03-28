from datetime import datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Collect(Base):
    """文章收藏表"""

    __tablename__ = "collect"

    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="用户ID")
    article_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="文章ID")
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="收藏时间",
    )
