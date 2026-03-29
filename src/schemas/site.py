from pydantic import BaseModel


class SiteInfo(BaseModel):
    ownerName: str | None
    ownerAvatar: str | None
    ownerBio: str | None
    articleCount: int
    categoryCount: int
    tagCount: int
