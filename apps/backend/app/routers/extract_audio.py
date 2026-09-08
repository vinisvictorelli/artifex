from fastapi import APIRouter
from pydantic import BaseModel

from artifex_core.extract_audio.extract_audio import extract_audio as extract_audio_core

router = APIRouter(prefix="/extract-audio", tags=["extract-audio"])


class ExtractAudioRequest(BaseModel):
    video_path: str
    output_path: str | None = None
    format: str = "wav"


@router.post("")
def extract_audio(request: ExtractAudioRequest):
    output = extract_audio_core(request.video_path, request.output_path, request.format)
    return {"output_path": output}
