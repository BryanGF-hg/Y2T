import subprocess
import tempfile
import os
import whisper

class TranscriptScrapeError(Exception):
    pass


def fetch_transcript_whisper(youtube_url: str) -> dict:
    """
    Descarga audio y lo transcribe con Whisper
    """
    with tempfile.TemporaryDirectory() as tmp:
        audio_path = os.path.join(tmp, "audio.wav")

        # 1️⃣ Descargar SOLO audio
        cmd = [
            "yt-dlp",
            "-f", "bestaudio",
            "-x",
            "--audio-format", "wav",
            "-o", audio_path,
            youtube_url,
        ]

        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )

        if not os.path.exists(audio_path):
            raise TranscriptScrapeError("No se pudo descargar el audio")

        # 2️⃣ Whisper
        model = whisper.load_model("base")  # base / small / medium
        result = model.transcribe(audio_path)

        text = result.get("text", "").strip()
        if not text:
            raise TranscriptScrapeError("Whisper no devolvió texto")

        return {
            "transcript": text,
            "source_lang": result.get("language", "unknown"),
            "source": "whisper",
        }
