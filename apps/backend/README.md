# Artifex Backend

API FastAPI local que expõe as ferramentas de `packages/core` (artifex_core) para o app desktop.

## Rodando

Na raiz do repositório:

```bash
poetry install
poetry run uvicorn app.main:app --reload --app-dir apps/backend
```

A API sobe em `http://127.0.0.1:8000`. Endpoints:

- `POST /downloader` — baixa um vídeo via yt-dlp
- `POST /extract-audio` — extrai áudio de um vídeo
- `POST /auto-caption` — gera legendas .srt via Whisper
- `POST /cutting-tool/auto-cut` — remove silêncios de um vídeo

## Empacotando para produção

O app desktop espera um binário standalone em `apps/backend/dist/artifex-backend`, gerado com
PyInstaller:

```bash
poetry run pyinstaller --onefile --name artifex-backend app/main.py
```

O `electron-builder` copia esse binário para os recursos do app (ver `electron-builder.yml`).
