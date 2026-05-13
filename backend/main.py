from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from artifex.auto_caption.auto_caption import mp3_to_srt

app = FastAPI()

# Permite acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/auto_caption")
def auto_caption(dados: dict):
    resultado = mp3_to_srt(dados["caminho_mp3"])
    return {"resultado": resultado}