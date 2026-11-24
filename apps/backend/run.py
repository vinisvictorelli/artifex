"""
Ponto de entrada do backend empacotado (PyInstaller).

Dois modos:
    artifex-backend                  sobe a API em 127.0.0.1:8000
    artifex-backend --yt-dlp <args>  roda o yt-dlp embutido (usado pelo downloader)

O segundo modo existe porque, no app instalado, não há um executável `yt-dlp`
no PATH: o próprio binário do backend faz esse papel.
"""

import multiprocessing
import os
import shutil
import sys
import tempfile

HOST = "127.0.0.1"
PORT = 8000


def _prepare_path() -> None:
    """Coloca no PATH o ffmpeg embutido (como `ffmpeg`) e o deno ao lado do binário."""
    extra: list[str] = [os.path.dirname(os.path.abspath(sys.executable))]

    try:
        import imageio_ffmpeg

        source = imageio_ffmpeg.get_ffmpeg_exe()
        shim_dir = tempfile.mkdtemp(prefix="artifex-ffmpeg-")
        shim = os.path.join(shim_dir, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        shutil.copy2(source, shim)  # cópia: symlinks exigem privilégio no Windows
        os.chmod(shim, 0o755)
        extra.append(shim_dir)
    except Exception as exc:  # sem ffmpeg o app abre, mas conversões falham
        print(f"[artifex] ffmpeg embutido indisponível: {exc}", file=sys.stderr)

    os.environ["PATH"] = os.pathsep.join([*extra, os.environ.get("PATH", "")])


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--yt-dlp":
        import yt_dlp

        sys.exit(yt_dlp.main(sys.argv[2:]))

    multiprocessing.freeze_support()
    _prepare_path()

    import uvicorn

    from app.main import app

    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    main()
