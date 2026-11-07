import threading

from dataclasses import asdict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app import jobs
from artifex_core.downloader.downloader import (
    DownloadCancelled,
    DownloadError,
    Progress,
    download_file,
    get_video_info,
)

router = APIRouter(prefix="/downloader", tags=["downloader"])


class DownloadRequest(BaseModel):
    url: str
    dest: str
    format: str = "mp4"
    height: int | None = Field(default=None, gt=0)


class InfoRequest(BaseModel):
    url: str


def _run(job: jobs.Job, request: DownloadRequest) -> None:
    def on_progress(p: Progress) -> None:
        job.phase, job.downloaded, job.total = p.phase, p.downloaded, p.total
        job.speed, job.eta = p.speed, p.eta

    try:
        output = download_file(
            request.url,
            request.dest,
            request.format,
            on_progress,
            job.cancel_event,
            request.height,
        )
        jobs.finish(job, "done", output_path=output, speed=None, eta=None)
    except DownloadCancelled:
        jobs.finish(job, "cancelled")
    except DownloadError as exc:
        jobs.finish(job, "error", error=str(exc))
    except Exception as exc:  # falha inesperada não pode deixar o job "running" para sempre
        jobs.finish(job, "error", error=f"{type(exc).__name__}: {exc}")


@router.post("/info")
def video_info(request: InfoRequest):
    # def síncrona: o FastAPI a executa em threadpool, sem bloquear o event loop.
    try:
        return asdict(get_video_info(request.url))
    except DownloadError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("")
def start_download(request: DownloadRequest):
    job = jobs.create()
    threading.Thread(target=_run, args=(job, request), daemon=True).start()
    return {"job_id": job.id}


def _get_or_404(job_id: str) -> jobs.Job:
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Download não encontrado")
    return job


@router.get("/{job_id}")
def download_status(job_id: str):
    return _get_or_404(job_id).to_dict()


@router.delete("/{job_id}")
def cancel_download(job_id: str):
    job = _get_or_404(job_id)
    job.cancel_event.set()
    return job.to_dict()
