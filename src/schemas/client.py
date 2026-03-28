from pydantic import BaseModel, ConfigDict


class ClientCreate(BaseModel):
    name: str
    description: str | None = None


class ClientUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ClientItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    clientId: str
    description: str | None

    @classmethod
    def from_orm(cls, obj) -> "ClientItem":
        return cls(
            id=obj.id,
            name=obj.name,
            clientId=obj.client_id,
            description=obj.description,
        )
