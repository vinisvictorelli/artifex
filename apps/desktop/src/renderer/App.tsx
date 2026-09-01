import { useEffect, useState } from "react";
import { Menu } from "lucide-react";
import { Sidebar } from "./components/Sidebar";
import { tools } from "./tools/registry";

const STORAGE_KEY = "artifex.activeTool";

export default function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [activeId, setActiveId] = useState<string>(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved && tools.some((t) => t.id === saved) ? saved : tools[0].id;
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, activeId);
  }, [activeId]);

  const active = tools.find((t) => t.id === activeId) ?? tools[0];
  const ActiveComponent = active.Component;

  return (
    <div className="min-h-screen flex flex-col">
      <Sidebar
        open={menuOpen}
        activeId={activeId}
        onSelect={(id) => {
          setActiveId(id);
          setMenuOpen(false);
        }}
        onClose={() => setMenuOpen(false)}
      />

      <header className="flex items-center gap-3 border-b border-white/5 px-4 py-3">
        <button
          type="button"
          onClick={() => setMenuOpen(true)}
          aria-label="Abrir menu"
          aria-expanded={menuOpen}
          className="rounded-md p-1.5 text-neutral-400 hover:bg-white/5 hover:text-neutral-200 transition-colors"
        >
          <Menu size={18} />
        </button>
        <div>
          <h1 className="text-sm font-semibold tracking-tight">{active.label}</h1>
          <p className="text-xs text-neutral-500">{active.description}</p>
        </div>
      </header>

      <main className="flex-1 p-6">
        <div className="mx-auto w-full max-w-xl">
          <ActiveComponent />
        </div>
      </main>
    </div>
  );
}
