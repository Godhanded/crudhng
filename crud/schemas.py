from pydantic import BaseModel, constr, EmailStr, validator


class RegisterSchema(BaseModel):
    name: str


class QuerySchema(BaseModel):
    user_id: int
