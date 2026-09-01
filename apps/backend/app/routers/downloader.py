from fastapi import APIRouter
from pydantic import BaseModel

from artifex_core.downloader.downloader import download_file

router = APIRouter(prefix="/downloader", tags=["downloader"])


class DownloadRequest(BaseModel):
    url: str
    dest: str
    format: str = "mp4"


@router.post("")
def download(request: DownloadRequest):
    output = download_file(request.url, request.dest, request.format)
    return {"output_path": output}
