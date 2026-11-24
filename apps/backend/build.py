"""
Empacota o backend com PyInstaller (modo onedir) em apps/backend/dist/artifex-backend/.

Uso (na raiz do repositório, com as dependências instaladas):
    python apps/backend/build.py                  # com Whisper (torch)
    python apps/backend/build.py --without-whisper  # sem Whisper (ex.: Mac Intel)

O resultado é copiado pelo electron-builder para os recursos do app. Além do
binário, a pasta recebe o deno, runtime JS que o yt-dlp usa para resolver os
desafios de assinatura do YouTube (o usuário final não precisa ter Node).
"""

import argparse
import io
import os
import platform
import shutil
import stat
import sys
import urllib.request
import zipfile

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(os.path.dirname(BACKEND_DIR))
DIST_DIR = os.path.join(BACKEND_DIR, "dist")
BUNDLE_DIR = os.path.join(DIST_DIR, "artifex-backend")

# Pacotes com dados/binários/imports dinâmicos que a análise do PyInstaller não enxerga.
COLLECT_ALL = ["yt_dlp", "yt_dlp_ejs", "imageio_ffmpeg", "imageio", "moviepy", "certifi", "speech_recognition"]
COLLECT_SUBMODULES = ["uvicorn", "app", "artifex_core"]
WHISPER_COLLECT_ALL = ["whisper", "tiktoken", "tiktoken_ext"]
# triton é só para GPU (quase 1 GB) e o app roda o torch em CPU.
EXCLUDES = ["tkinter", "matplotlib", "IPython", "pytest", "triton"]

DENO_ASSETS = {
    ("Linux", "x86_64"): "deno-x86_64-unknown-linux-gnu.zip",
    ("Darwin", "arm64"): "deno-aarch64-apple-darwin.zip",
    ("Darwin", "x86_64"): "deno-x86_64-apple-darwin.zip",
    ("Windows", "AMD64"): "deno-x86_64-pc-windows-msvc.zip",
}


def run_pyinstaller(with_whisper: bool) -> None:
    import PyInstaller.__main__ as pyi

    args = [
        os.path.join(BACKEND_DIR, "run.py"),
        "--noconfirm",
        "--clean",
        "--onedir",
        "--name", "artifex-backend",
        "--console",
        "--distpath", DIST_DIR,
        "--workpath", os.path.join(BACKEND_DIR, "build"),
        "--specpath", os.path.join(BACKEND_DIR, "build"),
        "--paths", BACKEND_DIR,
        "--paths", os.path.join(REPO_DIR, "packages", "core"),
    ]
    for pkg in COLLECT_ALL + (WHISPER_COLLECT_ALL if with_whisper else []):
        args += ["--collect-all", pkg]
    for pkg in COLLECT_SUBMODULES:
        args += ["--collect-submodules", pkg]
    for pkg in EXCLUDES + ([] if with_whisper else ["torch", "whisper"]):
        args += ["--exclude-module", pkg]
    pyi.run(args)


def bundle_deno() -> None:
    key = (platform.system(), platform.machine())
    asset = DENO_ASSETS.get(key)
    if asset is None:
        sys.exit(f"Plataforma sem deno mapeado: {key}")
    url = f"https://github.com/denoland/deno/releases/latest/download/{asset}"
    print(f"Baixando {url}")
    with urllib.request.urlopen(url, timeout=120) as resp:
        data = resp.read()
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        name = "deno.exe" if platform.system() == "Windows" else "deno"
        zf.extract(name, BUNDLE_DIR)
        os.chmod(os.path.join(BUNDLE_DIR, name), os.stat(os.path.join(BUNDLE_DIR, name)).st_mode | stat.S_IEXEC)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--without-whisper", action="store_true")
    parser.add_argument("--skip-deno", action="store_true", help="não baixa o deno (builds locais offline)")
    opts = parser.parse_args()

    shutil.rmtree(DIST_DIR, ignore_errors=True)
    run_pyinstaller(with_whisper=not opts.without_whisper)
    if not opts.skip_deno:
        bundle_deno()
    exe = "artifex-backend.exe" if os.name == "nt" else "artifex-backend"
    print(f"\nBackend empacotado em {os.path.join(BUNDLE_DIR, exe)}")


if __name__ == "__main__":
    main()
