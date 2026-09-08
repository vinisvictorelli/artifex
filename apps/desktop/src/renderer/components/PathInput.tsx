import { FolderOpen } from "lucide-react";

export type PathFilter = { name: string; extensions: string[] };

type PathInputProps = {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  /** Habilita o botão de explorador. Ausente = campo de texto puro (ex.: URL). */
  mode?: "file" | "directory" | "save";
  /** Filtros de extensão do diálogo nativo. */
  filters?: PathFilter[];
};

export function PathInput({ label, value, onChange, placeholder, mode, filters }: PathInputProps) {
  const bridge = typeof window !== "undefined" ? window.artifex : undefined;

  const canBrowse =
    mode === "file"
      ? !!bridge?.openFile
      : mode === "directory"
        ? !!bridge?.openDirectory
        : mode === "save"
          ? !!bridge?.saveFile
          : false;

  async function handleBrowse() {
    if (!bridge) return;
    const defaultPath = value || undefined;
    let picked: string | null = null;

    if (mode === "file" && bridge.openFile) {
      picked = await bridge.openFile({ title: label, filters, defaultPath });
    } else if (mode === "directory" && bridge.openDirectory) {
      picked = await bridge.openDirectory({ title: label, defaultPath });
    } else if (mode === "save" && bridge.saveFile) {
      picked = await bridge.saveFile({ title: label, filters, defaultPath });
    }

    if (picked) onChange(picked);
  }

  const browseLabel =
    mode === "directory"
      ? "Escolher pasta"
      : mode === "save"
        ? "Escolher onde salvar"
        : "Escolher arquivo";

  return (
    <label className="flex flex-col gap-1">
      <span className="text-[11px] text-neutral-500">{label}</span>
      <div className="flex gap-1.5">
        <input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="flex-1 rounded-md bg-surface border border-white/10 px-2.5 py-1.5 text-xs text-neutral-200 focus:outline-none focus:border-accent"
        />
        {canBrowse && (
          <button
            type="button"
            onClick={handleBrowse}
            aria-label={browseLabel}
            title={browseLabel}
            className="shrink-0 rounded-md border border-white/10 bg-surface px-2 text-neutral-400 hover:bg-white/5 hover:text-neutral-200 focus:outline-none focus:border-accent transition-colors"
          >
            <FolderOpen size={14} />
          </button>
        )}
      </div>
    </label>
  );
}
