import os

from moviepy import VideoFileClip, concatenate_videoclips
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

from artifex_core.extract_audio.extract_audio import extract_audio


def detect_speaking_segments(
    audio_path: str, silence_thresh: int = -35, min_silence_len: int = 1000
) -> list[tuple[float, float]]:
    """
    Detecta os segmentos de áudio onde há fala.

    Args:
        audio_path: Caminho do arquivo de áudio.
        silence_thresh: Limite de silêncio em decibéis. Mais baixo identifica mais silêncio.
        min_silence_len: Duração mínima do silêncio (ms) para considerar uma pausa.
    """
    audio = AudioSegment.from_file(audio_path)
    nonsilent_ranges = detect_nonsilent(
        audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh
    )
    return [(start / 1000, end / 1000) for start, end in nonsilent_ranges]


def edit_video(video_path: str, speaking_segments: list[tuple[float, float]], output_path: str) -> str:
    """Corta o vídeo com base nos segmentos de fala detectados."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with VideoFileClip(video_path) as clip:
        clips = [clip.subclipped(start, end) for start, end in speaking_segments]
        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(output_path)
    return output_path


def auto_cut(video_path: str, output_path: str) -> str:
    """Extrai áudio, detecta trechos com fala e gera o vídeo cortado."""
    audio_path = extract_audio(video_path)
    try:
        speaking_segments = detect_speaking_segments(audio_path)
        return edit_video(video_path, speaking_segments, output_path)
    finally:
        os.remove(audio_path)
