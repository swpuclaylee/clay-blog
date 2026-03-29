from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, field_serializer


class EmailCodeRequest(BaseModel):
    email: EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    code: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginData(BaseModel):
    token: str


class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nickname: str | None
    username: str
    email: str | None
    avatar: str | None
    bio: str | None  # mapped from brief
    role: str

    @classmethod
    def from_orm(cls, user) -> "UserInfo":
        return cls(
            id=user.id,
            nickname=user.nickname,
            username=user.username,
            email=user.email,
            avatar=user.avatar,
            bio=user.brief,
            role=user.role,
        )


class UpdateUserRequest(BaseModel):
    nickname: str | None = None
    avatar: str | None = None
    bio: str | None = None


class ChangePasswordRequest(BaseModel):
    oldPassword: str
    newPassword: str


class BindEmailRequest(BaseModel):
    email: EmailStr
    code: str


class UserListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nickname: str | None
    email: str | None
    avatar: str | None
    role: str
    status: int
    createTime: datetime

    @field_serializer("createTime")
    def serialize_dt(self, dt: datetime, _info) -> str:
        return dt.strftime("%Y-%m-%dT%H:%M:%S")

    @classmethod
    def from_orm(cls, user) -> "UserListItem":
        return cls(
            id=user.id,
            nickname=user.nickname,
            email=user.email,
            avatar=user.avatar,
            role=user.role,
            status=user.status,
            createTime=user.created_at,
        )


class UpdateUserStatusRequest(BaseModel):
    userId: int
    status: Literal[0, 1]  # 0=正常 1=封禁


class UpdateUserRoleRequest(BaseModel):
    userId: int
    role: Literal["admin", "user"]
