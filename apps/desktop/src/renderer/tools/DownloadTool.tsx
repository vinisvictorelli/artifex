import { useState } from "react";
import { ToolCard } from "../components/ToolCard";
import { PathInput } from "../components/PathInput";
import { api } from "../lib/api";

export function DownloadTool() {
  const [url, setUrl] = useState("");
  const [dest, setDest] = useState("");

  return (
    <ToolCard
      title="Baixar vídeo"
      description="Baixa um vídeo a partir de uma URL usando yt-dlp."
      runLabel="Baixar"
      onRun={() => api.download({ url, dest })}
    >
      <PathInput label="URL" value={url} onChange={setUrl} placeholder="https://..." />
      <PathInput label="Destino" value={dest} onChange={setDest} placeholder="./downloads/video.mp4" />
    </ToolCard>
  );
}
