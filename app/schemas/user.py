from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    auth0_sub: str


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    auth0_sub: str

    model_config = {"from_attributes": True}
