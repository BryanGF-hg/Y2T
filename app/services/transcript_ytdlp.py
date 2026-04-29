import subprocess
import tempfile
import os
import re


class TranscriptScrapeError(Exception):
    pass


def _clean_vtt(vtt_text: str) -> str:
    lines = []
    for line in vtt_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("WEBVTT"):
            continue
        if "-->" in line:
            continue
        if re.match(r"^\d+$", line):
            continue
        lines.append(line)
    return "\n".join(lines)


def _run_ytdlp(cmd: list[str], tmp: str) -> list[str]:
    """
    Ejecuta yt-dlp y devuelve los archivos .vtt generados
    """
    subprocess.run(
        cmd,
        cwd=tmp,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return [f for f in os.listdir(tmp) if f.endswith(".vtt")]


def fetch_transcript_ytdlp(youtube_url: str, langs=None) -> dict:
    if not langs:
        langs = ["es", "en"]

    with tempfile.TemporaryDirectory() as tmp:

        base_cmd = [
            "yt-dlp",
            "--skip-download",
            "--sub-format", "vtt",
            "--sub-lang", ",".join(langs),
            "--no-check-formats",
            "--ignore-errors",
            "--extractor-args", "youtube:player_client=web",
            "--cookies-from-browser", "firefox",
            "--sleep-interval", "3",
            "--max-sleep-interval", "6",
            "--retries", "5",
            youtube_url,
        ]

        # 1️⃣ INTENTO: subtítulos MANUALES
        try:
            cmd_manual = base_cmd + ["--write-sub"]
            vtt_files = _run_ytdlp(cmd_manual, tmp)

            if vtt_files:
                return _load_vtt(tmp, vtt_files, source="manual")

        except Exception:
            pass  # seguimos al siguiente intento

        # 2️⃣ INTENTO: subtítulos AUTOMÁTICOS
        try:
            cmd_auto = base_cmd + ["--write-auto-sub"]
            vtt_files = _run_ytdlp(cmd_auto, tmp)

            if vtt_files:
                return _load_vtt(tmp, vtt_files, source="auto")

        except Exception:
            pass

        # ❌ NADA FUNCIONÓ
        raise TranscriptScrapeError(
            "No hay subtítulos disponibles (manuales ni automáticos) para este video"
        )


def _load_vtt(tmp: str, files: list[str], source: str) -> dict:
    """
    Carga el primer VTT válido y lo devuelve limpio
    """
    files.sort(key=lambda f: "auto" in f.lower())

    vtt_path = os.path.join(tmp, files[0])
    with open(vtt_path, "r", encoding="utf-8") as fh:
        transcript = _clean_vtt(fh.read())

    if not transcript.strip():
        raise TranscriptScrapeError("El archivo de subtítulos está vacío")

    return {
        "title": None,
        "transcript": transcript,
        "source": f"youtube_captions_{source}",
        "file": files[0],
    }
