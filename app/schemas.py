from pydantic import BaseModel, HttpUrl
from typing import Optional

class VideoCreate(BaseModel):
    youtube_url: str
    target_lang: Optional[str] = None

class VideoUpdate(BaseModel):
    title: Optional[str] = None
    source_lang: Optional[str] = None
    target_lang: Optional[str] = None
    transcript: Optional[str] = None
    transcript_translated: Optional[str] = None

class VideoOut(BaseModel):
    id: int
    youtube_url: str
    title: Optional[str] = None
    source_lang: Optional[str] = None
    target_lang: Optional[str] = None
    transcript: Optional[str] = None
    transcript_translated: Optional[str] = None

    class Config:
        from_attributes = True

