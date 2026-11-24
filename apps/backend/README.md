# Artifex Backend

API FastAPI local que expõe as ferramentas de `packages/core` (artifex_core) para o app desktop.

## Rodando

Na raiz do repositório:

```bash
poetry install
poetry run uvicorn app.main:app --reload --app-dir apps/backend
```

A API sobe em `http://127.0.0.1:8000`. Endpoints:

- `POST /downloader` — inicia o download via yt-dlp e devolve `{job_id}`
- `GET /downloader/{job_id}` — progresso (`status`, `phase`, `downloaded`, `total`, `percent`, `speed`, `eta`)
- `DELETE /downloader/{job_id}` — cancela o download e apaga os arquivos parciais
- `POST /extract-audio` — extrai áudio de um vídeo
- `POST /convert-image` — converte uma imagem entre formatos (PNG, JPEG, GIF, WebP, BMP, TIFF, ICO, TGA, PDF, AVIF)
- `POST /auto-caption` — gera legendas .srt via Whisper
- `POST /cutting-tool/auto-cut` — remove silêncios de um vídeo

## Empacotando para produção

O app desktop espera o backend empacotado em `apps/backend/dist/artifex-backend/` (PyInstaller,
modo onedir), copiado para os recursos do app pelo `electron-builder`:

```bash
poetry run pip install pyinstaller
poetry run python apps/backend/build.py                 # com Whisper
poetry run python apps/backend/build.py --without-whisper   # sem torch (ex.: Mac Intel)
```

O ponto de entrada é `run.py` (sobe a API em `127.0.0.1:8000`). O mesmo binário também serve de
`yt-dlp` (`artifex-backend --yt-dlp <args>`), e o `build.py` embute o deno, usado pelo yt-dlp para
o YouTube, de modo que o usuário final não precisa de Node, yt-dlp nem ffmpeg instalados.
