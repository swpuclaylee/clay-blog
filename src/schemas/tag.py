from pydantic import BaseModel, ConfigDict


class TagCreate(BaseModel):
    name: str


class TagUpdate(BaseModel):
    name: str


class TagItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    articleCount: int = 0
