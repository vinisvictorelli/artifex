# Artifex

Ferramentas de automação para produção de vídeo, empacotadas como aplicativo desktop (Electron).

## Estrutura

```
apps/
  desktop/     # Electron + React (UI)
  backend/     # API FastAPI local, consumida pela UI
packages/
  core/        # Lógica de processamento de vídeo/áudio (Python), sem dependência de UI
```

- `packages/core` (`artifex_core`) contém as ferramentas: download (yt-dlp), extração de áudio,
  legendas automáticas (Whisper) e corte automático por silêncio (moviepy/pydub).
- `apps/backend` expõe cada ferramenta como endpoint FastAPI (`/downloader`, `/extract-audio`,
  `/auto-caption`, `/cutting-tool/auto-cut`).
- `apps/desktop` é o app Electron: sobe o backend localmente e renderiza a UI React que chama
  esses endpoints.

## Rodando em desenvolvimento

### Backend (Python / Poetry)

```bash
poetry install
poetry run uvicorn app.main:app --reload --app-dir apps/backend
```

### Desktop (Electron / React)

```bash
cd apps/desktop
npm install
npm run dev
```

Isso sobe o Vite (renderer) e o Electron juntos. Em desenvolvimento, o backend Python roda
separadamente (comando acima) — o Electron só assume o processo do backend em builds de produção.

## Build de produção

```bash
cd apps/desktop
npm run build
```

Empacota o backend (via PyInstaller — ver `apps/backend/README.md`) como recurso do app e gera o
instalador via `electron-builder`.
