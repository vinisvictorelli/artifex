import subprocess

# Formatos que representam apenas a trilha de áudio: nesses casos o yt-dlp
# baixa somente o áudio (-x) e converte para o formato pedido.
AUDIO_FORMATS = {"mp3", "m4a", "aac", "opus", "flac", "wav"}


def download_file(url: str, dest: str, format: str = "mp4") -> str:
    """
    Baixa um vídeo (ou apenas o áudio) usando yt-dlp.

    Args:
        url: URL do vídeo.
        dest: Caminho de saída do arquivo baixado.
        format: Container de vídeo (mp4, mkv, webm) ou formato de áudio
            (mp3, m4a, ...). Para formatos de áudio, baixa somente a trilha
            de áudio.

    Returns:
        Caminho do arquivo baixado (dest).
    """
    if format in AUDIO_FORMATS:
        args = ["yt-dlp", "-x", "--audio-format", format, "-o", dest, url]
    else:
        args = [
            "yt-dlp",
            "-f",
            "bv*+ba/b",
            "--merge-output-format",
            format,
            "-o",
            dest,
            url,
        ]

    subprocess.run(args, check=True, capture_output=True, text=True)
    return dest
