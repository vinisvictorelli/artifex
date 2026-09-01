import os
import tempfile

from moviepy import VideoFileClip


def extract_audio(video_path: str, output_path: str | None = None) -> str:
    """
    Extrai o áudio de um vídeo e salva como arquivo .wav.

    Args:
        video_path: Caminho do arquivo de vídeo de entrada.
        output_path: Caminho de saída para o áudio. Se não informado,
            usa um arquivo temporário do sistema.

    Returns:
        Caminho do arquivo de áudio gerado.
    """
    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix=".wav", prefix="artifex_audio_")
        os.close(fd)
    else:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with VideoFileClip(video_path) as clip:
        clip.audio.write_audiofile(output_path, codec="pcm_s16le")

    return output_path
