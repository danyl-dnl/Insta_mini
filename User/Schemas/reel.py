from pydantic import BaseModel

class ReelCreate(BaseModel):
    video_url: str
    caption: str | None = None
