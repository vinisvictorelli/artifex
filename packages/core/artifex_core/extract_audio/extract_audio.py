import os
import tempfile

from moviepy import VideoFileClip

# Codec do ffmpeg por formato de saída. O container é inferido pela extensão
# do arquivo; aqui só escolhemos o codec de áudio correspondente.
_CODEC_BY_FORMAT = {
    "wav": "pcm_s16le",
    "mp3": "libmp3lame",
    "aac": "aac",
    "m4a": "aac",
    "flac": "flac",
    "ogg": "libvorbis",
}


def extract_audio(
    video_path: str, output_path: str | None = None, format: str = "wav"
) -> str:
    """
    Extrai o áudio de um vídeo.

    Args:
        video_path: Caminho do arquivo de vídeo de entrada.
        output_path: Caminho de saída para o áudio. Se não informado, usa um
            arquivo temporário do sistema com a extensão do formato.
        format: Formato do áudio de saída (wav, mp3, aac, flac, ogg).

    Returns:
        Caminho do arquivo de áudio gerado.
    """
    codec = _CODEC_BY_FORMAT.get(format, "pcm_s16le")

    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix=f".{format}", prefix="artifex_audio_")
        os.close(fd)
    else:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with VideoFileClip(video_path) as clip:
        clip.audio.write_audiofile(output_path, codec=codec)

    return output_path
