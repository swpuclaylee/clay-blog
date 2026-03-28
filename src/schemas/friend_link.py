from pydantic import BaseModel, ConfigDict


class FriendLinkCreate(BaseModel):
    name: str
    url: str
    avatar: str | None = None
    description: str | None = None


class FriendLinkUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    avatar: str | None = None
    description: str | None = None


class FriendLinkItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    avatar: str | None
    description: str | None
