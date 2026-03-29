from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db, require_admin
from src.core.config import settings
from src.core.security import create_access_token
from src.models.user import User
from src.schemas.base import ResponseModel
from src.schemas.common import PageResult
from src.schemas.user import (
    BindEmailRequest,
    ChangePasswordRequest,
    EmailCodeRequest,
    LoginData,
    LoginRequest,
    RegisterRequest,
    UpdateUserRequest,
    UpdateUserRoleRequest,
    UpdateUserStatusRequest,
    UserInfo,
    UserListItem,
)
from src.services.user import UserService
from src.utils.email import send_email_code, verify_email_code

router = APIRouter(prefix="/user", tags=["用户"])


@router.post("/email/code", response_model=ResponseModel[None], summary="发送邮箱验证码")
async def send_code(body: EmailCodeRequest, db: AsyncSession = Depends(get_db)):
    await send_email_code(body.email)
    return ResponseModel(message="验证码已发送")


@router.post("/register", response_model=ResponseModel[None], summary="用户注册")
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if len(body.password) < 6:
        return ResponseModel(code=0, message="密码长度至少 6 位")
    service = UserService(db)
    existing = await service.get_by_email(body.email)
    if existing:
        return ResponseModel(code=0, message="该邮箱已注册")
    ok = await verify_email_code(body.email, body.code)
    if not ok:
        return ResponseModel(code=0, message="验证码错误或已过期")
    await service.register(email=body.email, password=body.password)
    return ResponseModel(message="注册成功")


@router.post("/login", response_model=ResponseModel[LoginData], summary="用户登录")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.authenticate(body.email, body.password)
    if not user:
        return ResponseModel(code=0, message="邮箱或密码错误")
    if not user.is_active:
        return ResponseModel(code=0, message="账号已被封禁")
    await UserService(db).update_last_login(user.id)
    token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return ResponseModel(message="登录成功", data=LoginData(token=token))


@router.post("/logout", response_model=ResponseModel[None], summary="退出登录")
async def logout(current_user: User = Depends(get_current_user)):
    return ResponseModel(message="退出成功")


@router.get("/info", response_model=ResponseModel[UserInfo], summary="获取当前用户信息")
async def get_info(current_user: User = Depends(get_current_user)):
    return ResponseModel(data=UserInfo.from_orm(current_user))


@router.put("/info", response_model=ResponseModel[None], summary="更新用户信息")
async def update_info(
    body: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    await service.update_info(current_user, body.nickname, body.avatar, body.bio)
    return ResponseModel(message="更新成功")


@router.put("/password", response_model=ResponseModel[None], summary="修改密码")
async def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    ok = await service.change_password(current_user, body.oldPassword, body.newPassword)
    if not ok:
        return ResponseModel(code=0, message="原密码错误")
    return ResponseModel(message="修改成功")


@router.post("/email/bind", response_model=ResponseModel[None], summary="绑定/更换邮箱")
async def bind_email(
    body: BindEmailRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ok = await verify_email_code(body.email, body.code)
    if not ok:
        return ResponseModel(code=0, message="验证码错误或已过期")
    service = UserService(db)
    success = await service.bind_email(current_user, body.email)
    if not success:
        return ResponseModel(code=0, message="该邮箱已被其他账号使用")
    return ResponseModel(message="绑定成功")


@router.get(
    "/page",
    response_model=ResponseModel[PageResult[UserListItem]],
    summary="分页查询用户列表（管理员）",
)
async def get_user_page(
    page: int = 1,
    size: int = 20,
    keyword: str | None = None,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    result = await service.get_page(page, size, keyword)
    return ResponseModel(data=result)


@router.put("/role", response_model=ResponseModel[None], summary="修改用户角色（管理员）")
async def update_role(
    body: UpdateUserRoleRequest,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    ok = await service.update_role(body.userId, body.role)
    if not ok:
        return ResponseModel(code=0, message="用户不存在")
    return ResponseModel(message="操作成功")


@router.put("/status", response_model=ResponseModel[None], summary="更新用户状态（管理员）")
async def update_status(
    body: UpdateUserStatusRequest,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    ok = await service.update_status(body.userId, body.status)
    if not ok:
        return ResponseModel(code=0, message="用户不存在")
    return ResponseModel(message="操作成功")
