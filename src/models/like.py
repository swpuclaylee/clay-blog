from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Like(Base):
    """文章点赞表"""

    __tablename__ = "like"

    article_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="文章ID")
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="用户ID")
