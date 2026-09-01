from fastapi import APIRouter
from pydantic import BaseModel

from artifex_core.cutting_tool.smart_cutting_tool import auto_cut

router = APIRouter(prefix="/cutting-tool", tags=["cutting-tool"])


class AutoCutRequest(BaseModel):
    video_path: str
    output_path: str


@router.post("/auto-cut")
def auto_cut_endpoint(request: AutoCutRequest):
    output = auto_cut(request.video_path, request.output_path)
    return {"output_path": output}
