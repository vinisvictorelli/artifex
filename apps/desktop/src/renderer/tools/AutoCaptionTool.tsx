import { useState } from "react";
import { ToolCard } from "../components/ToolCard";
import { PathInput } from "../components/PathInput";
import { api } from "../lib/api";

export function AutoCaptionTool() {
  const [audioPath, setAudioPath] = useState("");
  const [outputPath, setOutputPath] = useState("");

  return (
    <ToolCard
      title="Legendas automáticas"
      description="Gera um arquivo .srt a partir de um áudio, usando Whisper."
      runLabel="Gerar legendas"
      onRun={() => api.autoCaption({ audio_path: audioPath, output_path: outputPath })}
    >
      <PathInput label="Áudio de entrada" value={audioPath} onChange={setAudioPath} placeholder="./audio.wav" />
      <PathInput label="SRT de saída" value={outputPath} onChange={setOutputPath} placeholder="./legenda.srt" />
    </ToolCard>
  );
}
