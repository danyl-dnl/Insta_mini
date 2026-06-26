from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None
    profile_picture: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    profile_picture: str | None = None


class UserBioCreate(BaseModel):
    bio_text: str
    is_active: bool = False


class UserBioUpdate(BaseModel):
    bio_text: str | None = None
    is_active: bool | None = None


class PrivacyHistoryCreate(BaseModel):
    privacy_type: str
    is_active: bool = False


class PrivacyHistoryUpdate(BaseModel):
    is_active: bool | None = None
