from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class CategoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    articleCount: int = 0
    description: str | None = None
