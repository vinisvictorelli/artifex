import os
import re
import shutil
import subprocess
import threading
from collections import deque
from dataclasses import dataclass
from typing import Callable

# Formatos que representam apenas a trilha de áudio: nesses casos o yt-dlp
# baixa somente o áudio (-x) e converte para o formato pedido.
AUDIO_FORMATS = {"mp3", "m4a", "aac", "opus", "flac", "wav"}

_PROGRESS_PREFIX = "ARTIFEX"
_PROGRESS_TEMPLATE = (
    f"download:{_PROGRESS_PREFIX} %(progress.downloaded_bytes)s %(progress.total_bytes)s "
    "%(progress.total_bytes_estimate)s %(progress.speed)s %(progress.eta)s"
)


class DownloadError(RuntimeError):
    """Falha do yt-dlp, com a mensagem de erro dele."""


class DownloadCancelled(Exception):
    """O download foi cancelado pelo usuário."""


@dataclass
class Progress:
    # preparing | video | audio | download | merging
    phase: str = "preparing"
    downloaded: int = 0
    total: int | None = None
    speed: float | None = None
    eta: int | None = None


def _number(token: str) -> float | None:
    try:
        return float(token)
    except ValueError:  # "NA"
        return None


def parse_progress_line(line: str) -> tuple[int, int | None, float | None, int | None] | None:
    """
    Lê uma linha do template de progresso do yt-dlp.

    Returns:
        (baixado, total, velocidade, eta) ou None se não for uma linha de progresso.
        O total usa o tamanho exato quando existe, senão o estimado.
    """
    parts = line.split()
    if len(parts) != 6 or parts[0] != _PROGRESS_PREFIX:
        return None
    downloaded, total, estimate, speed, eta = (_number(p) for p in parts[1:])
    total = total or estimate
    return (
        int(downloaded or 0),
        int(total) if total else None,
        speed,
        int(eta) if eta is not None else None,
    )


def _base_args() -> list[str]:
    # O yt-dlp só habilita o Deno por padrão; o YouTube exige um runtime JS
    # para resolver os desafios de assinatura (senão as URLs retornam 403).
    args = ["yt-dlp"]
    if shutil.which("node"):
        args += ["--js-runtimes", "node"]
    return args


def _build_args(url: str, dest: str, format: str) -> list[str]:
    if format in AUDIO_FORMATS:
        return [*_base_args(), "-x", "--audio-format", format, "-o", dest, url]
    return [
        *_base_args(),
        "-f",
        "bv*+ba/b",
        "--merge-output-format",
        format,
        "-o",
        dest,
        url,
    ]


def _expected_size(args: list[str]) -> int | None:
    """Consulta o tamanho total (exato ou aproximado) sem baixar nada."""
    # Reaproveita os argumentos do download, trocando só o -o/URL por --simulate.
    query = [
        *args[:-1],
        "--simulate",
        "--no-warnings",
        "--print",
        "%(filesize,filesize_approx)s",
        args[-1],
    ]
    try:
        out = subprocess.run(query, capture_output=True, text=True, timeout=60).stdout
    except (subprocess.TimeoutExpired, OSError):
        return None
    for token in reversed(out.split()):
        value = _number(token)
        if value:
            return int(value)
    return None


def _remove_partials(dest: str) -> None:
    """Apaga arquivos parciais do yt-dlp (.part, .ytdl e trilhas .fNNN) deixados por um cancelamento."""
    directory = os.path.dirname(dest) or "."
    name = os.path.basename(dest)
    root = os.path.splitext(name)[0]
    pattern = re.compile(
        rf"^(?:{re.escape(name)}\.(?:part|ytdl)|{re.escape(root)}\.f\d+\.\w+(?:\.(?:part|ytdl))?)$"
    )
    try:
        entries = os.listdir(directory)
    except OSError:
        return
    for entry in entries:
        if pattern.match(entry):
            try:
                os.remove(os.path.join(directory, entry))
            except OSError:
                pass


def download_file(
    url: str,
    dest: str,
    format: str = "mp4",
    on_progress: Callable[[Progress], None] | None = None,
    cancel_event: threading.Event | None = None,
) -> str:
    """
    Baixa um vídeo (ou apenas o áudio) usando yt-dlp.

    Args:
        url: URL do vídeo.
        dest: Caminho de saída do arquivo baixado.
        format: Container de vídeo (mp4, mkv, webm) ou formato de áudio
            (mp3, m4a, ...). Para formatos de áudio, baixa somente a trilha
            de áudio.
        on_progress: Chamado a cada atualização. O progresso é acumulado
            entre as trilhas (vídeo + áudio), então nunca retrocede.
        cancel_event: Quando sinalizado, interrompe o download, apaga os
            arquivos parciais e levanta DownloadCancelled.

    Returns:
        Caminho do arquivo baixado (dest).
    """
    report = on_progress or (lambda _p: None)
    cancel = cancel_event or threading.Event()
    args = _build_args(url, dest, format)

    progress = Progress()
    report(progress)
    progress.total = _expected_size(args)
    if cancel.is_set():
        raise DownloadCancelled()
    report(progress)

    if os.path.dirname(dest):
        os.makedirs(os.path.dirname(dest), exist_ok=True)

    proc = subprocess.Popen(
        [*args[:-1], "--newline", "--progress-template", _PROGRESS_TEMPLATE, args[-1]],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    finished = threading.Event()

    def _watch_cancel() -> None:
        while not finished.is_set():
            if cancel.wait(0.2):
                if proc.poll() is None:
                    proc.terminate()
                return

    threading.Thread(target=_watch_cancel, daemon=True).start()

    tail: deque[str] = deque(maxlen=50)
    parts_total = 1  # quantas trilhas serão baixadas (ex.: 399+251 = 2)
    part_index = 0  # trilha atual (1-based)
    completed = 0  # bytes das trilhas já concluídas
    part_downloaded = 0
    part_total: int | None = None
    known_total = progress.total

    try:
        assert proc.stdout is not None
        for raw in proc.stdout:
            line = raw.strip()
            if not line:
                continue
            tail.append(line)

            parsed = parse_progress_line(line)
            if parsed:
                part_downloaded, part_total, progress.speed, progress.eta = parsed
                progress.downloaded = completed + part_downloaded
                if known_total is None:
                    # Sem total prévio: soma o que já se sabe, nunca abaixo do baixado.
                    est = completed + (part_total or 0)
                    progress.total = est if part_total else None
                else:
                    progress.total = max(known_total, progress.downloaded)
                report(progress)
                continue

            if line.startswith("[info]") and "Downloading" in line and "format(s):" in line:
                ids = line.rsplit(":", 1)[-1].strip()
                parts_total = max(1, len(ids.split("+")))
            elif line.startswith("[download] Destination:"):
                if part_index:
                    completed += part_total or part_downloaded
                part_index += 1
                part_downloaded, part_total = 0, None
                if format in AUDIO_FORMATS or parts_total == 1:
                    progress.phase = "audio" if format in AUDIO_FORMATS else "download"
                else:
                    progress.phase = "video" if part_index == 1 else "audio"
                report(progress)
            elif line.startswith(("[Merger]", "[ExtractAudio]", "[VideoRemuxer]", "[VideoConvertor]")):
                progress.phase = "merging"
                progress.speed = progress.eta = None
                report(progress)

        code = proc.wait()
    finally:
        finished.set()
        if proc.poll() is None:
            proc.kill()
        proc.stdout.close()

    if cancel.is_set():
        _remove_partials(dest)
        raise DownloadCancelled()

    if code != 0:
        errors = [l for l in tail if l.startswith("ERROR")]
        raise DownloadError(errors[-1] if errors else "\n".join(list(tail)[-5:]) or f"yt-dlp saiu com código {code}")

    progress.phase = "merging"
    progress.downloaded = progress.total or progress.downloaded
    progress.speed = progress.eta = None
    report(progress)
    return dest
