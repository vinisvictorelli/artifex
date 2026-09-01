import { useState } from "react";
import { ToolCard } from "../components/ToolCard";
import { PathInput } from "../components/PathInput";
import { api } from "../lib/api";

export function ExtractAudioTool() {
  const [videoPath, setVideoPath] = useState("");
  const [outputPath, setOutputPath] = useState("");

  return (
    <ToolCard
      title="Extrair áudio"
      description="Extrai a trilha de áudio de um vídeo em formato .wav."
      runLabel="Extrair"
      onRun={() => api.extractAudio({ video_path: videoPath, output_path: outputPath || undefined })}
    >
      <PathInput label="Vídeo de entrada" value={videoPath} onChange={setVideoPath} placeholder="./video.mp4" />
      <PathInput label="Áudio de saída (opcional)" value={outputPath} onChange={setOutputPath} placeholder="./audio.wav" />
    </ToolCard>
  );
}
