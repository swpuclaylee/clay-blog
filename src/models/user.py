from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base
from src.models.mixins import TimestampMixin


class User(TimestampMixin, Base):
    """用户表"""

    __tablename__ = "user"

    username: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, comment="用户名"
    )
    password: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="密码（bcrypt）"
    )
    nickname: Mapped[str] = mapped_column(String(64), nullable=True, comment="昵称")
    gender: Mapped[int] = mapped_column(SmallInteger, nullable=True, comment="性别：1男 0女")
    birthday: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="生日"
    )
    email: Mapped[str | None] = mapped_column(
        String(128), unique=True, nullable=True, comment="邮箱"
    )
    brief: Mapped[str | None] = mapped_column(
        String(256), nullable=True, comment="个性签名"
    )
    avatar: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="头像路径（MinIO key）"
    )
    # status: 0=正常 1=锁定 2=禁用 3=过期
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, comment="状态"
    )
    # admin: 1=管理员 0=普通用户
    admin: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, comment="是否管理员"
    )

    @property
    def role(self) -> str:
        return "admin" if self.admin == 1 else "user"

    @property
    def is_active(self) -> bool:
        return self.status == 0
