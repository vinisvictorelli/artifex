<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/assets/logo-light.svg">
  <img alt="Artifex" src="docs/assets/logo-light.svg" height="56">
</picture>

<br><br>

**Automação inteligente para produção de vídeo, num app desktop.**<br>
Baixe, extraia, legende, corte e converta — tudo local, sem enviar seus arquivos para a nuvem.

<br>

[![Release](https://img.shields.io/github/v/release/vinisvictorelli/artifex?style=flat-square&color=0A0A0A&label=vers%C3%A3o)](https://github.com/vinisvictorelli/artifex/releases)
[![Licença](https://img.shields.io/badge/licen%C3%A7a-GPLv3-0A0A0A?style=flat-square)](LICENSE)
![Plataformas](https://img.shields.io/badge/plataformas-Linux%20%C2%B7%20macOS%20%C2%B7%20Windows-0A0A0A?style=flat-square)
![Electron](https://img.shields.io/badge/Electron-44-0A0A0A?style=flat-square&logo=electron&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12%2B-0A0A0A?style=flat-square&logo=python&logoColor=white)

[**Baixar**](https://github.com/vinisvictorelli/artifex/releases) · [Funcionalidades](#-funcionalidades) · [Instalação](#-instalação) · [Desenvolvimento](#-desenvolvimento) · [Contribuindo](#-contribuindo)

</div>

<br>

## ✦ Funcionalidades

| | Ferramenta | O que faz |
| :-: | --- | --- |
| ⬇️ | **Baixar vídeo** | Baixa vídeos a partir de uma URL com [yt-dlp](https://github.com/yt-dlp/yt-dlp), com progresso, velocidade, ETA e cancelamento. |
| 🎧 | **Extrair áudio** | Extrai a trilha de áudio de qualquer vídeo. |
| 💬 | **Legendas automáticas** | Gera legendas `.srt` com [Whisper](https://github.com/openai/whisper), rodando localmente. |
| ✂️ | **Corte automático** | Detecta e remove os silêncios do vídeo. |
| 🖼️ | **Converter imagem** | Converte entre PNG, JPEG, GIF, WebP, BMP, TIFF, ICO, TGA, PDF e AVIF, com controle de qualidade. |

**Por que Artifex?**

- 🔒 **Privado** — todo o processamento acontece na sua máquina.
- 📦 **Tudo incluso** — o instalador já traz o backend, o ffmpeg e o runtime que o yt-dlp precisa. Não há nada para instalar à parte.
- 🧩 **Modular** — cada ferramenta é independente, o que facilita adicionar novas.

## ⬇ Instalação

Baixe o instalador do seu sistema na página de [**Releases**](https://github.com/vinisvictorelli/artifex/releases):

| Sistema | Arquivo | Como instalar |
| --- | --- | --- |
| **Linux** | `Artifex-*-linux-x64.AppImage` | `chmod +x Artifex-*.AppImage && ./Artifex-*.AppImage` |
| **macOS** (Apple Silicon e Intel) | `Artifex-*-mac-*.dmg` | Abra o `.dmg` e arraste o Artifex para *Applications*. |
| **Windows** | `Artifex-*-win-x64.exe` | Execute o instalador. |

> [!NOTE]
> Os instaladores **ainda não são assinados**.
> - **macOS:** na primeira abertura, escolha *Abrir mesmo assim* ou rode `xattr -cr /Applications/Artifex.app`.
> - **Windows:** o SmartScreen mostra um aviso; clique em *Mais informações → Executar assim mesmo*.

> [!IMPORTANT]
> - O modelo do Whisper é baixado na **primeira legenda** gerada (precisa de internet).
> - O **Mac Intel** sai **sem legendas automáticas**, pois o PyTorch não publica binários para Intel. As demais ferramentas funcionam normalmente.

## 🏗 Arquitetura

```
┌──────────────────────┐   HTTP (localhost)   ┌──────────────────────┐
│  apps/desktop        │ ───────────────────▶ │  apps/backend        │
│  Electron + React    │                      │  FastAPI             │
└──────────────────────┘                      └──────────┬───────────┘
                                                         │
                                              ┌──────────▼───────────┐
                                              │  packages/core       │
                                              │  artifex_core        │
                                              └──────────────────────┘
```

```
apps/
  desktop/     # Electron + React + Tailwind (UI)
  backend/     # API FastAPI local, consumida pela UI
packages/
  core/        # Lógica de vídeo/áudio/imagem (Python), sem dependência de UI
tests/         # Testes do core e da API
```

- **`packages/core`** (`artifex_core`) — download (yt-dlp), extração de áudio, legendas (Whisper),
  corte por silêncio (moviepy/pydub) e conversão de imagem (Pillow).
- **`apps/backend`** — expõe cada ferramenta como endpoint (`/downloader`, `/extract-audio`,
  `/auto-caption`, `/cutting-tool/auto-cut`, `/convert-image`). Veja o [README do backend](apps/backend/README.md).
- **`apps/desktop`** — app Electron que sobe o backend localmente e renderiza a UI React.

## 🛠 Desenvolvimento

**Requisitos:** Node.js 22+, Python 3.12+ e [Poetry](https://python-poetry.org/).

```bash
git clone https://github.com/vinisvictorelli/artifex.git
cd artifex
npm run setup        # poetry install && npm install
npm run dev          # backend + desktop juntos
```

Ou separadamente:

```bash
npm run dev:backend  # FastAPI em http://127.0.0.1:8000 (com reload)
npm run dev:desktop  # Vite + Electron
```

Em desenvolvimento o Electron **não** sobe o backend sozinho — isso só acontece nos builds de produção.

### Testes

```bash
poetry run python -m unittest discover -s tests -t . -v   # core e API
npm test --workspace apps/desktop      # UI
```

### Build local

Empacota só o sistema em que você está:

```bash
poetry run pip install pyinstaller
poetry run python apps/backend/build.py    # --without-whisper para pular o torch
npm run build
```

Os instaladores aparecem em `apps/desktop/release/`.

### Release

Os instaladores de todos os sistemas são gerados pelo GitHub Actions
(`.github/workflows/release.yml`). A tag precisa ser igual à versão de `apps/desktop/package.json`:

```bash
git tag v0.1.0 && git push origin v0.1.0
```

O workflow testa, empacota o backend e o app em cada sistema e abre um **rascunho de release**
para você revisar e publicar. Em *Actions → Release → Run workflow* ele roda sem criar release
(os instaladores ficam como artefatos do job).

## 🤝 Contribuindo

Contribuições são bem-vindas! Abra uma [issue](https://github.com/vinisvictorelli/artifex/issues)
para relatar um problema ou sugerir uma ferramenta, ou envie um pull request. Para adicionar uma
ferramenta nova: crie a lógica em `packages/core`, exponha-a em um router de `apps/backend` e
registre a tela em `apps/desktop/src/renderer/tools/registry.tsx`.

## 📄 Licença

Distribuído sob a licença [GNU GPLv3](LICENSE).

<div align="center">
<br>
<img src="docs/assets/icon.png" alt="" height="48">
<br>
<sub>Feito por <a href="https://github.com/vinisvictorelli">vinisvictorelli</a></sub>
</div>
