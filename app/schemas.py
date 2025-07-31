from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    last_name: str
    role: str = "user"

class UserLogin(BaseModel):
    email: EmailStr
    password: str
