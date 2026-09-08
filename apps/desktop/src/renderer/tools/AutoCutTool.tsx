import { useState } from "react";
import { ToolCard } from "../components/ToolCard";
import { PathInput } from "../components/PathInput";
import { FormatSelect } from "../components/FormatSelect";
import { api } from "../lib/api";
import { AUTO_CUT_FORMATS, VIDEO_FILTERS, filtersForFormat, swapExtension } from "../lib/pathFilters";

export function AutoCutTool() {
  const [videoPath, setVideoPath] = useState("");
  const [outputPath, setOutputPath] = useState("");
  const [format, setFormat] = useState(AUTO_CUT_FORMATS[0].value);

  function handleFormatChange(next: string) {
    setFormat(next);
    setOutputPath((prev) => (prev ? swapExtension(prev, next) : prev));
  }

  return (
    <ToolCard
      title="Corte automático"
      description="Remove silêncios de um vídeo, mantendo apenas os trechos com fala."
      runLabel="Cortar"
      onRun={() => api.autoCut({ video_path: videoPath, output_path: outputPath, format })}
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
        label="Formato de saída"
        value={format}
        options={AUTO_CUT_FORMATS}
        onChange={handleFormatChange}
      />
      <PathInput
        label="Vídeo de saída"
        value={outputPath}
        onChange={setOutputPath}
        placeholder="./video_editado.mp4"
        mode="save"
        filters={filtersForFormat(format)}
      />
    </ToolCard>
  );
}
