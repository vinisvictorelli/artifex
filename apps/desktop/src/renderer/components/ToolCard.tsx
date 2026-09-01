import { ReactNode, useState } from "react";

type ToolCardProps = {
  title: string;
  description: string;
  children: ReactNode;
  onRun: () => Promise<unknown>;
  runLabel?: string;
};

export function ToolCard({ title, description, children, onRun, runLabel = "Executar" }: ToolCardProps) {
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

      <div className="flex items-center gap-3">
        <button
          onClick={handleRun}
          disabled={status === "running"}
          className="rounded-md bg-accent px-3 py-1.5 text-xs font-medium text-white hover:bg-accent/90 disabled:opacity-50 transition-colors"
        >
          {status === "running" ? "Executando..." : runLabel}
        </button>
        {status === "done" && <span className="text-xs text-emerald-400">Concluído</span>}
        {status === "error" && <span className="text-xs text-red-400">Erro</span>}
      </div>

      {message && <p className="text-[11px] text-neutral-500 break-all">{message}</p>}
    </div>
  );
}
