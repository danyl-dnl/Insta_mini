from pydantic import BaseModel


class RoleCreate(BaseModel):
    role_name: str


class RoleUpdate(BaseModel):
    role_name: str
