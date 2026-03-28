from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str


class MessageReply(BaseModel):
    messageId: int
    content: str


class UserBrief(BaseModel):
    id: int
    nickname: str | None
    avatar: str | None


class MessageReplyItem(BaseModel):
    id: int
    content: str
    user: UserBrief


class MessageItem(BaseModel):
    id: int
    content: str
    createTime: str
    user: UserBrief
    replies: list[MessageReplyItem] = []
