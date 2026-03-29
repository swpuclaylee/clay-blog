
from pydantic import BaseModel, ConfigDict, field_serializer


class CategoryBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class TagBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class AuthorBrief(BaseModel):
    id: int
    nickname: str | None
    avatar: str | None


class ArticleCreate(BaseModel):
    title: str
    content: str | None = None
    summary: str | None = None
    cover: str | None = None
    categoryId: int | None = None
    tagIds: list[int] = []
    status: int = 0


class ArticleUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    summary: str | None = None
    cover: str | None = None
    categoryId: int | None = None
    tagIds: list[int] | None = None
    status: int | None = None


class ArticleStatusUpdate(BaseModel):
    status: int


class ArticleListItem(BaseModel):
    id: int
    title: str
    summary: str | None
    cover: str | None
    category: CategoryBrief | None
    tags: list[TagBrief]
    viewCount: int
    likeCount: int
    collectCount: int
    commentCount: int
    createTime: str

    @field_serializer("createTime")
    def serialize_dt(self, v: str, _info) -> str:
        return v


class ArticleDetail(BaseModel):
    id: int
    title: str
    content: str | None
    summary: str | None
    cover: str | None
    status: int
    viewCount: int
    likeCount: int
    collectCount: int
    commentCount: int
    category: CategoryBrief | None
    tags: list[TagBrief]
    author: AuthorBrief
    createTime: str
    updateTime: str


class ArticleAdminItem(BaseModel):
    id: int
    title: str
    category: CategoryBrief | None
    status: int
    viewCount: int
    createTime: str


class ArticleIdResponse(BaseModel):
    id: int


class RecommendItem(BaseModel):
    id: str
    title: str
    score: float


class ArticleRelatedItem(BaseModel):
    id: int
    title: str
    cover: str | None
    createTime: str
