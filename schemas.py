from pydantic import BaseModel,EmailStr
from email_validator import EmailNotValidError

class RoleCreate(BaseModel):
    role_name: str


class RoleUpdate(BaseModel):
    role_name: str


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None
    profile_picture: str | None = None


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


class PostCreate(BaseModel):
    user_id: int
    caption: str
    image_url: str


class PostUpdate(BaseModel):
    caption: str


class PostLikeCreate(BaseModel):
    user_id: int


class CommentCreate(BaseModel):
    user_id: int
    comment_text: str


class CommentUpdate(BaseModel):
    comment_text: str


class StoryCreate(BaseModel):
    user_id: int
    media_url: str


class HighlightCreate(BaseModel):
    user_id: int
    title: str
    cover_url: str | None = None


class HighlightUpdate(BaseModel):
    title: str | None = None
    cover_url: str | None = None
