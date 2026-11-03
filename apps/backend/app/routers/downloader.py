import threading

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app import jobs
from artifex_core.downloader.downloader import (
    DownloadCancelled,
    DownloadError,
    Progress,
    download_file,
)

router = APIRouter(prefix="/downloader", tags=["downloader"])


class DownloadRequest(BaseModel):
    url: str
    dest: str
    format: str = "mp4"


def _run(job: jobs.Job, request: DownloadRequest) -> None:
    def on_progress(p: Progress) -> None:
        job.phase, job.downloaded, job.total = p.phase, p.downloaded, p.total
        job.speed, job.eta = p.speed, p.eta

    try:
        output = download_file(
            request.url, request.dest, request.format, on_progress, job.cancel_event
        )
        jobs.finish(job, "done", output_path=output, speed=None, eta=None)
    except DownloadCancelled:
        jobs.finish(job, "cancelled")
    except DownloadError as exc:
        jobs.finish(job, "error", error=str(exc))
    except Exception as exc:  # falha inesperada não pode deixar o job "running" para sempre
        jobs.finish(job, "error", error=f"{type(exc).__name__}: {exc}")


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
