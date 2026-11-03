import { ReactNode, useState } from "react";

type ToolCardProps = {
  title: string;
  description: string;
  children: ReactNode;
  onRun: () => Promise<unknown>;
  runLabel?: string;
  /** Conteúdo exibido entre os campos e o botão (ex.: barra de progresso). */
  progress?: ReactNode;
  /** Quando informado, aparece um botão "Cancelar" durante a execução. */
  onCancel?: () => void;
  /** Mantém o botão desabilitado por um trabalho em andamento iniciado fora do card. */
  busy?: boolean;
};

export function ToolCard({ title, description, children, onRun, runLabel = "Executar", progress, onCancel, busy = false }: ToolCardProps) {
  const [status, setStatus] = useState<"idle" | "running" | "done" | "error">("idle");
  const [message, setMessage] = useState("");

  async function handleRun() {
    setStatus("running");
    setMessage("");
    try {
      const result = await onRun();
      setStatus("done");
      setMessage(JSON.stringify(result));
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : "Erro desconhecido");
    }
  }

  return (
    <div className="rounded-xl border border-white/5 bg-panel p-5 flex flex-col gap-4">
      <div>
        <h2 className="text-sm font-medium text-neutral-100">{title}</h2>
        <p className="text-xs text-neutral-500 mt-1">{description}</p>
      </div>

      <div className="flex flex-col gap-2">{children}</div>

      {progress}

      <div className="flex items-center gap-3">
        <button
          onClick={handleRun}
          disabled={status === "running" || busy}
          className="rounded-md bg-accent px-3 py-1.5 text-xs font-medium text-white hover:bg-accent/90 disabled:opacity-50 transition-colors"
        >
          {status === "running" || busy ? "Executando..." : runLabel}
        </button>
        {onCancel && (status === "running" || busy) && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-md border border-white/10 px-3 py-1.5 text-xs text-neutral-300 hover:bg-white/5 transition-colors"
          >
            Cancelar
          </button>
        )}
        {status === "done" && <span className="text-xs text-emerald-400">Concluído</span>}
        {status === "error" && <span className="text-xs text-red-400">Erro</span>}
      </div>

      {message && <p className="text-[11px] text-neutral-500 break-all">{message}</p>}
    </div>
  );
}
