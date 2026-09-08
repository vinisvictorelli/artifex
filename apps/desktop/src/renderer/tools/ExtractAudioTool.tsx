import { useState } from "react";
import { ToolCard } from "../components/ToolCard";
import { PathInput } from "../components/PathInput";
import { FormatSelect } from "../components/FormatSelect";
import { api } from "../lib/api";
import {
  EXTRACT_AUDIO_FORMATS,
  VIDEO_FILTERS,
  filtersForFormat,
  swapExtension,
} from "../lib/pathFilters";

export function ExtractAudioTool() {
  const [videoPath, setVideoPath] = useState("");
  const [outputPath, setOutputPath] = useState("");
  const [format, setFormat] = useState(EXTRACT_AUDIO_FORMATS[0].value);

  function handleFormatChange(next: string) {
    setFormat(next);
    setOutputPath((prev) => (prev ? swapExtension(prev, next) : prev));
  }

  return (
    <ToolCard
      title="Extrair áudio"
      description="Extrai a trilha de áudio de um vídeo."
      runLabel="Extrair"
      onRun={() =>
        api.extractAudio({ video_path: videoPath, output_path: outputPath || undefined, format })
      }
    >
      <PathInput
        label="Vídeo de entrada"
        value={videoPath}
        onChange={setVideoPath}
        placeholder="./video.mp4"
        mode="file"
        filters={VIDEO_FILTERS}
      />
      <FormatSelect
        label="Formato do áudio"
        value={format}
        options={EXTRACT_AUDIO_FORMATS}
        onChange={handleFormatChange}
      />
      <PathInput
        label="Áudio de saída (opcional)"
        value={outputPath}
        onChange={setOutputPath}
        placeholder="./audio.wav"
        mode="save"
        filters={filtersForFormat(format)}
      />
    </ToolCard>
  );
}
