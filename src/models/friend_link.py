from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class FriendLink(Base):
    """友链表"""

    __tablename__ = "friend_link"

    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="博客名称")
    url: Mapped[str] = mapped_column(String(512), nullable=False, comment="链接")
    avatar: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="头像（icon）"
    )
    description: Mapped[str | None] = mapped_column(
        String(256), nullable=True, comment="简介"
    )
