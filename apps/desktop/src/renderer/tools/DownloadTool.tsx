import { useState } from "react";
import { ToolCard } from "../components/ToolCard";
import { PathInput } from "../components/PathInput";
import { FormatSelect } from "../components/FormatSelect";
import { api } from "../lib/api";
import { DOWNLOAD_FORMATS, filtersForFormat, swapExtension } from "../lib/pathFilters";

export function DownloadTool() {
  const [url, setUrl] = useState("");
  const [dest, setDest] = useState("");
  const [format, setFormat] = useState(DOWNLOAD_FORMATS[0].value);

  function handleFormatChange(next: string) {
    setFormat(next);
    setDest((prev) => (prev ? swapExtension(prev, next) : prev));
  }

  return (
    <ToolCard
      title="Baixar vídeo"
      description="Baixa um vídeo a partir de uma URL usando yt-dlp."
      runLabel="Baixar"
      onRun={() => api.download({ url, dest, format })}
    >
      <PathInput label="URL" value={url} onChange={setUrl} placeholder="https://..." />
      <FormatSelect
        label="Formato de saída"
        value={format}
        options={DOWNLOAD_FORMATS}
        onChange={handleFormatChange}
      />
      <PathInput
        label="Destino"
        value={dest}
        onChange={setDest}
        placeholder="./downloads/video.mp4"
        mode="save"
        filters={filtersForFormat(format)}
      />
    </ToolCard>
  );
}
