from pydantic import BaseModel


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
