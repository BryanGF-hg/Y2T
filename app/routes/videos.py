from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Video
from ..schemas import VideoCreate, VideoUpdate, VideoOut

from ..services.transcript_ytdlp import fetch_transcript_ytdlp, TranscriptScrapeError as CaptionError
from ..services.transcript_whisper import fetch_transcript_whisper, TranscriptScrapeError as WhisperError
from ..services.translator import translate_text

router = APIRouter(prefix="/api/videos", tags=["videos"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=list[VideoOut])
def list_videos(db: Session = Depends(get_db)):
    return db.query(Video).order_by(Video.updated_at.desc()).all()

@router.post("", response_model=VideoOut)
def create_video(payload: VideoCreate, db: Session = Depends(get_db)):
    # upsert simple por URL
    existing = db.query(Video).filter(Video.youtube_url == payload.youtube_url).first()
    if existing:
        return existing

    v = Video(youtube_url=payload.youtube_url, target_lang=payload.target_lang)
    db.add(v)
    db.commit()
    db.refresh(v)
    return v

@router.put("/{video_id}", response_model=VideoOut)
def update_video(video_id: int, payload: VideoUpdate, db: Session = Depends(get_db)):
    v = db.query(Video).get(video_id)
    if not v:
        raise HTTPException(404, "No existe")
    for k, val in payload.model_dump(exclude_unset=True).items():
        setattr(v, k, val)
    db.commit()
    db.refresh(v)
    return v

@router.delete("/{video_id}")
def delete_video(video_id: int, db: Session = Depends(get_db)):
    v = db.query(Video).get(video_id)
    if not v:
        raise HTTPException(404, "No existe")
    db.delete(v)
    db.commit()
    return {"ok": True}


@router.post("/{video_id}/scrape")
def scrape_transcript(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).get(video_id)
    if not video:
        raise HTTPException(404, "Video no encontrado")

    # 1️⃣ Intento: captions
    try:
        data = fetch_transcript_ytdlp(video.youtube_url)
        video.transcript = data["transcript"]
        video.source_lang = "auto"
        video.transcript_status = "completed"

        db.commit()
        return video

    except CaptionError:
        pass  # seguimos a Whisper

    # 2️⃣ Intento: Whisper
    try:
        data = fetch_transcript_whisper(video.youtube_url)
        video.transcript = data["transcript"]
        video.source_lang = data["source_lang"]
        video.transcript_status = "completed"

        db.commit()
        return video

    except WhisperError:
        # 3️⃣ FALLO TOTAL → marcar como pendiente
        video.transcript_status = "pending"
        db.commit()

        raise HTTPException(
            status_code=202,
            detail="No hay captions y Whisper falló. Video marcado como pending_transcript."
        )

