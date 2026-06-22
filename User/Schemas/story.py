from pydantic import BaseModel


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
