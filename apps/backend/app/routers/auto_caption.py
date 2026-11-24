from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from artifex_core.auto_caption.auto_caption import WhisperUnavailable, mp3_to_srt

router = APIRouter(prefix="/auto-caption", tags=["auto-caption"])


class AutoCaptionRequest(BaseModel):
    audio_path: str
    output_path: str
    max_chars_per_segment: int = 42
    model_size: str = "medium"


@router.post("")
def auto_caption(request: AutoCaptionRequest):
    try:
        output = mp3_to_srt(
            request.audio_path,
            request.output_path,
            max_chars_per_segment=request.max_chars_per_segment,
            model_size=request.model_size,
        )
    except WhisperUnavailable as exc:
        raise HTTPException(status_code=501, detail=str(exc))
    return {"output_path": output}
