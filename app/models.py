from sqlalchemy import Column, Integer, String, Text, DateTime, func
from .db import Base
import enum

class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(String(500), nullable=True)
    
    
class TranscriptStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True)
    youtube_url = Column(String(500), unique=True, nullable=False)
    title = Column(String(300), nullable=True)

    transcript = Column(Text)
    source_lang = Column(String(10))
    target_lang = Column(String(20), nullable=True)

    transcript_status = Column(
        String(20),
        default="pending",
        nullable=False
    )

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

