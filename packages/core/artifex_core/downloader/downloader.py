import subprocess


def download_file(url: str, dest: str, format: str = "mp4") -> str:
    """
    Baixa um vídeo usando yt-dlp.

    Args:
        url: URL do vídeo.
        dest: Caminho de saída do arquivo baixado.
        format: Formato/container desejado.

    Returns:
        Caminho do arquivo baixado (dest).
    """
    subprocess.run(
        ["yt-dlp", "-o", dest, "-f", format, url],
        check=True,
        capture_output=True,
        text=True,
    )
    return dest
