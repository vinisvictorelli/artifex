import { contextBridge, ipcRenderer } from "electron";

// Ponte mínima e segura entre o renderer e o processo principal.
// A UI fala com o backend via HTTP (localhost); além disso, o preload
// expõe apenas os diálogos nativos de arquivo/pasta (por IPC) — nenhum
// acesso a fs/child_process é exposto ao renderer.
type DialogFilter = { name: string; extensions: string[] };

contextBridge.exposeInMainWorld("artifex", {
  backendUrl: "http://127.0.0.1:8000",

  // Escolher um arquivo existente (entrada).
  openFile: (opts: { title?: string; filters?: DialogFilter[]; defaultPath?: string } = {}) =>
    ipcRenderer.invoke("dialog:openFile", opts) as Promise<string | null>,

  // Escolher uma pasta.
  openDirectory: (opts: { title?: string; defaultPath?: string } = {}) =>
    ipcRenderer.invoke("dialog:openDirectory", opts) as Promise<string | null>,

  // Escolher onde salvar — o usuário digita o nome do arquivo.
  saveFile: (opts: { title?: string; filters?: DialogFilter[]; defaultPath?: string } = {}) =>
    ipcRenderer.invoke("dialog:saveFile", opts) as Promise<string | null>,
});
