from pydantic import BaseModel


class CommentCreate(BaseModel):
    articleId: int
    content: str


class ReplyCreate(BaseModel):
    commentId: int
    content: str


class UserBrief(BaseModel):
    id: int
    nickname: str | None
    avatar: str | None


class ReplyItem(BaseModel):
    id: int
    content: str
    createTime: str
    user: UserBrief


class CommentItem(BaseModel):
    id: int
    content: str
    createTime: str
    user: UserBrief
    replies: list[ReplyItem] = []


class AdminCommentItem(BaseModel):
    id: int
    content: str
    createTime: str
    user: UserBrief
    article: dict  # {"title": "..."}


class AdminReplyCommentArticle(BaseModel):
    id: int
    title: str


class AdminReplyComment(BaseModel):
    id: int
    content: str
    article: AdminReplyCommentArticle


class AdminReplyItem(BaseModel):
    id: int
    content: str
    createTime: str
    user: UserBrief
    comment: AdminReplyComment
