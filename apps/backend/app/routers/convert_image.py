from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from artifex_core.convert_image.convert_image import convert_image as convert_image_core

router = APIRouter(prefix="/convert-image", tags=["convert-image"])


class ConvertImageRequest(BaseModel):
    image_path: str
    output_path: str | None = None
    format: str = "png"
    quality: int = 90


@router.post("")
def convert_image(request: ConvertImageRequest):
    try:
        output = convert_image_core(
            request.image_path, request.output_path, request.format, request.quality
        )
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"output_path": output}
