import { useEffect, useRef, useState } from "react";
import { ToolCard } from "../components/ToolCard";
import { PathInput } from "../components/PathInput";
import { FormatSelect } from "../components/FormatSelect";
import { ProgressBar } from "../components/ProgressBar";
import { useJobProgress } from "../hooks/useJobProgress";
import { api, type VideoInfo } from "../lib/api";
import {
  DOWNLOAD_FORMATS,
  filtersForFormat,
  isAudioDownloadFormat,
  swapExtension,
  type FormatOption,
} from "../lib/pathFilters";

const PHASE_LABELS: Record<string, string> = {
  preparing: "Preparando...",
  video: "Baixando vídeo",
  audio: "Baixando áudio",
  download: "Baixando",
  merging: "Finalizando arquivo...",
};

const BEST = "best";
const HTTP_URL = /^https?:\/\//i;

type InfoState = "idle" | "loading" | "ready" | "error";

function formatSize(bytes: number): string {
  const mb = bytes / (1024 * 1024);
  return mb >= 1024 ? `${(mb / 1024).toFixed(1)} GB` : `${Math.round(mb)} MB`;
}

export function DownloadTool() {
  const [url, setUrl] = useState("");
  const [dest, setDest] = useState("");
  const [format, setFormat] = useState(DOWNLOAD_FORMATS[0].value);
  const [infoState, setInfoState] = useState<InfoState>("idle");
  const [info, setInfo] = useState<VideoInfo | null>(null);
  const [infoError, setInfoError] = useState("");
  const [quality, setQuality] = useState(BEST);
  const requestId = useRef(0);
  const { job, active, track, cancel } = useJobProgress("download", {
    status: api.downloadStatus,
    cancel: api.downloadCancel,
  });

  async function fetchInfo(target: string) {
    const id = ++requestId.current;
    setInfoState("loading");
    setInfo(null);
    setQuality(BEST);
    try {
      const result = await api.downloadInfo(target);
      if (id !== requestId.current) return; // resposta de uma URL antiga
      setInfo(result);
      setInfoState("ready");
    } catch (err) {
      if (id !== requestId.current) return;
      setInfoError(err instanceof Error ? err.message : String(err));
      setInfoState("error");
    }
  }

  // Ao mudar a URL, descarta o resultado anterior e consulta de novo após uma pausa na digitação.
  useEffect(() => {
    const target = url.trim();
    requestId.current++;
    setInfo(null);
    setQuality(BEST);
    setInfoState("idle");
    if (!HTTP_URL.test(target)) return;
    const timer = setTimeout(() => fetchInfo(target), 600);
    return () => clearTimeout(timer);
  }, [url]);

  const isAudio = isAudioDownloadFormat(format);
  const qualityOptions: FormatOption[] = [
    { value: BEST, label: "Melhor disponível" },
    ...(info?.qualities ?? []).map((q) => ({
      value: String(q.height),
      label: q.size ? `${q.label} · ~${formatSize(q.size)}` : q.label,
    })),
  ];

  function handleFormatChange(next: string) {
    setFormat(next);
    setDest((prev) => (prev ? swapExtension(prev, next) : prev));
  }

  async function handleRun() {
    const { job_id } = await api.downloadStart({
      url,
      dest,
      format,
      height: !isAudio && quality !== BEST ? Number(quality) : undefined,
    });
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
      {HTTP_URL.test(url.trim()) && infoState !== "loading" && infoState !== "ready" && (
        <button
          type="button"
          onClick={() => fetchInfo(url.trim())}
          className="self-start rounded-md border border-white/10 px-2.5 py-1 text-[11px] text-neutral-300 hover:bg-white/5 transition-colors"
        >
          Buscar qualidades
        </button>
      )}
      {infoState === "loading" && (
        <p className="text-[11px] text-neutral-500">Buscando qualidades...</p>
      )}
      {infoState === "error" && (
        <p className="text-[11px] text-red-400">
          {infoError} — o download usará a melhor qualidade.
        </p>
      )}
      {info?.title && <p className="truncate text-[11px] text-neutral-400">{info.title}</p>}
      <FormatSelect
        label="Formato de saída"
        value={format}
        options={DOWNLOAD_FORMATS}
        onChange={handleFormatChange}
      />
      {!isAudio && infoState === "ready" && (
        <FormatSelect
          label="Qualidade"
          value={quality}
          options={qualityOptions}
          onChange={setQuality}
        />
      )}
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
