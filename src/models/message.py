from datetime import datetime

from sqlalchemy import DateTime, Integer, SmallInteger, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Message(Base):
    """留言表（含回复，用 pid 区分）"""

    __tablename__ = "message"

    pid: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="父ID，留言时为null"
    )
    from_user_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="留言/回复者ID"
    )
    to_user_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="被回复者ID，留言时为null"
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="内容")
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )
    deleted: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, comment="是否删除：1是 0否"
    )
