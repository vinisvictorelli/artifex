import { useEffect } from "react";
import { tools } from "../tools/registry";

type SidebarProps = {
  open: boolean;
  activeId: string;
  onSelect: (id: string) => void;
  onClose: () => void;
};

export function Sidebar({ open, activeId, onSelect, onClose }: SidebarProps) {
  useEffect(() => {
    if (!open) return;
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/40"
          aria-hidden="true"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed left-0 top-0 z-50 flex h-full w-64 flex-col border-r border-white/5 bg-panel transition-transform duration-200 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
        aria-hidden={!open}
      >
        <div className="border-b border-white/5 px-5 py-4">
          <p className="text-sm font-semibold tracking-tight">Artifex</p>
          <p className="text-xs text-neutral-500">Automação de produção de vídeo</p>
        </div>

        <nav className="flex flex-col gap-1 p-2">
          {tools.map((tool) => {
            const Icon = tool.icon;
            const isActive = tool.id === activeId;
            return (
              <button
                key={tool.id}
                type="button"
                onClick={() => onSelect(tool.id)}
                aria-current={isActive ? "page" : undefined}
                className={`flex items-start gap-3 rounded-md px-3 py-2 text-left transition-colors ${
                  isActive
                    ? "bg-accent/10 text-neutral-100"
                    : "text-neutral-400 hover:bg-white/5 hover:text-neutral-200"
                }`}
              >
                <Icon size={16} className={`mt-0.5 shrink-0 ${isActive ? "text-accent" : ""}`} />
                <span className="flex flex-col">
                  <span className="text-xs font-medium">{tool.label}</span>
                  <span className="text-[11px] text-neutral-500">{tool.description}</span>
                </span>
              </button>
            );
          })}
        </nav>
      </aside>
    </>
  );
}
