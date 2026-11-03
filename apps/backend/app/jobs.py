import threading
import time
import uuid
from dataclasses import dataclass, field

# Jobs finalizados são descartados depois deste tempo.
_RETENTION_SECONDS = 3600


@dataclass
class Job:
    id: str
    status: str = "running"  # running | done | error | cancelled
    phase: str = "preparing"
    downloaded: int = 0
    total: int | None = None
    speed: float | None = None
    eta: int | None = None
    output_path: str | None = None
    error: str | None = None
    finished_at: float | None = None
    cancel_event: threading.Event = field(default_factory=threading.Event)

    def to_dict(self) -> dict:
        percent = None
        if self.total:
            percent = min(100.0, self.downloaded / self.total * 100)
        if self.status == "done":
            percent = 100.0
        return {
            "job_id": self.id,
            "status": self.status,
            "phase": self.phase,
            "downloaded": self.downloaded,
            "total": self.total,
            "percent": percent,
            "speed": self.speed,
            "eta": self.eta,
            "output_path": self.output_path,
            "error": self.error,
        }


_jobs: dict[str, Job] = {}
_lock = threading.Lock()


def _purge() -> None:
    now = time.time()
    for job_id in [
        j.id for j in _jobs.values() if j.finished_at and now - j.finished_at > _RETENTION_SECONDS
    ]:
        del _jobs[job_id]


def create() -> Job:
    with _lock:
        _purge()
        job = Job(id=uuid.uuid4().hex)
        _jobs[job.id] = job
        return job


def get(job_id: str) -> Job | None:
    with _lock:
        return _jobs.get(job_id)


def finish(job: Job, status: str, **fields) -> None:
    with _lock:
        job.status = status
        job.finished_at = time.time()
        for key, value in fields.items():
            setattr(job, key, value)
