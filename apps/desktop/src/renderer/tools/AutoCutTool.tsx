import { useState } from "react";
import { ToolCard } from "../components/ToolCard";
import { PathInput } from "../components/PathInput";
import { api } from "../lib/api";

export function AutoCutTool() {
  const [videoPath, setVideoPath] = useState("");
  const [outputPath, setOutputPath] = useState("");

  return (
    <ToolCard
      title="Corte automático"
      description="Remove silêncios de um vídeo, mantendo apenas os trechos com fala."
      runLabel="Cortar"
      onRun={() => api.autoCut({ video_path: videoPath, output_path: outputPath })}
    >
      <PathInput label="Vídeo de entrada" value={videoPath} onChange={setVideoPath} placeholder="./video.mp4" />
      <PathInput label="Vídeo de saída" value={outputPath} onChange={setOutputPath} placeholder="./video_editado.mp4" />
    </ToolCard>
  );
}
