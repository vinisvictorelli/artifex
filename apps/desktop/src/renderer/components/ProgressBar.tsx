import { formatBytes, formatEta } from "../lib/format";

type ProgressBarProps = {
  /** 0–100. Null = total desconhecido (barra indeterminada). */
  percent: number | null;
  /** Rótulo da etapa atual (ex.: "Baixando vídeo"). */
  label?: string;
  downloaded?: number;
  total?: number | null;
  /** Bytes por segundo. */
  speed?: number | null;
  /** Segundos restantes. */
  eta?: number | null;
  /** Sem total nem avanço (ex.: etapa final): barra animada. */
  indeterminate?: boolean;
};

export function ProgressBar({
  percent,
  label,
  downloaded,
  total,
  speed,
  eta,
  indeterminate = false,
}: ProgressBarProps) {
  const unknown = indeterminate || percent === null;
  const clamped = Math.max(0, Math.min(100, percent ?? 0));

  const sizeText =
    downloaded !== undefined && total
      ? `${formatBytes(downloaded)} / ${formatBytes(total)}`
      : downloaded
        ? formatBytes(downloaded)
        : total
          ? formatBytes(total)
          : "";

  const stats = [
    unknown ? null : `${clamped.toFixed(0)}%`,
    sizeText,
    speed ? `${formatBytes(speed)}/s` : null,
    eta != null ? `ETA ${formatEta(eta)}` : null,
  ].filter(Boolean);

  return (
    <div className="flex flex-col gap-1.5">
      {label && <span className="text-[11px] text-neutral-400">{label}</span>}
      <div
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={unknown ? undefined : Math.round(clamped)}
        aria-label={label ?? "Progresso"}
        className="relative h-2 w-full overflow-hidden rounded-full bg-surface border border-white/10"
      >
        {unknown ? (
          <div className="absolute inset-y-0 w-1/3 animate-pulse rounded-full bg-accent/70" />
        ) : (
          <div
            className="h-full rounded-full bg-accent transition-[width] duration-300 ease-out"
            style={{ width: `${clamped}%` }}
          />
        )}
      </div>
      {stats.length > 0 && (
        <span className="text-[11px] text-neutral-500 tabular-nums">{stats.join(" · ")}</span>
      )}
    </div>
  );
}
