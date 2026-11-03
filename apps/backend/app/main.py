from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auto_caption, convert_image, cutting_tool, downloader, extract_audio

app = FastAPI(title="Artifex API")

# O app Electron carrega a UI a partir de um esquema local (file:// ou
# um dev-server em localhost); liberamos CORS pois o backend só escuta
# em localhost e não é exposto publicamente.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auto_caption.router)
app.include_router(convert_image.router)
app.include_router(cutting_tool.router)
app.include_router(downloader.router)
app.include_router(extract_audio.router)


@app.get("/health")
def health():
    return {"status": "ok"}
