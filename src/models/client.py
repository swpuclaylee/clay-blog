import secrets

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Client(Base):
    """客户端表"""

    __tablename__ = "client"

    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="客户端名称")
    client_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        default=lambda: secrets.token_hex(16),
        comment="客户端ID（自动生成）",
    )
    description: Mapped[str | None] = mapped_column(
        String(256), nullable=True, comment="描述"
    )
