import { useState } from "react";
import { ToolCard } from "../components/ToolCard";
import { PathInput } from "../components/PathInput";
import { FormatSelect } from "../components/FormatSelect";
import { ProgressBar } from "../components/ProgressBar";
import { useJobProgress } from "../hooks/useJobProgress";
import { api } from "../lib/api";
import { DOWNLOAD_FORMATS, filtersForFormat, swapExtension } from "../lib/pathFilters";

const PHASE_LABELS: Record<string, string> = {
  preparing: "Preparando...",
  video: "Baixando vídeo",
  audio: "Baixando áudio",
  download: "Baixando",
  merging: "Finalizando arquivo...",
};

export function DownloadTool() {
  const [url, setUrl] = useState("");
  const [dest, setDest] = useState("");
  const [format, setFormat] = useState(DOWNLOAD_FORMATS[0].value);
  const { job, active, track, cancel } = useJobProgress("download", {
    status: api.downloadStatus,
    cancel: api.downloadCancel,
  });

  function handleFormatChange(next: string) {
    setFormat(next);
    setDest((prev) => (prev ? swapExtension(prev, next) : prev));
  }

  async function handleRun() {
    const { job_id } = await api.downloadStart({ url, dest, format });
    const done = await track(job_id);
    return { output_path: done.output_path };
  }

  const showBar = job !== null && (active || job.status === "done");
  const indeterminate = job?.phase === "preparing" || job?.phase === "merging";

  return (
    <ToolCard
      title="Baixar vídeo"
      description="Baixa um vídeo a partir de uma URL usando yt-dlp."
      runLabel="Baixar"
      onRun={handleRun}
      busy={active}
      onCancel={cancel}
      progress={
        showBar && job ? (
          <ProgressBar
            percent={job.status === "done" ? 100 : job.percent}
            label={job.status === "done" ? "Download concluído" : PHASE_LABELS[job.phase]}
            downloaded={job.downloaded}
            total={job.total}
            speed={job.speed}
            eta={job.eta}
            indeterminate={job.status !== "done" && indeterminate}
          />
        ) : null
      }
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
