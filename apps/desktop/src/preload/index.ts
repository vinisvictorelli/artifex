import { contextBridge } from "electron";

// Ponte mínima e segura entre o renderer e o processo principal.
// A UI fala com o backend via HTTP (localhost), então hoje o preload
// só expõe metadados do ambiente — nenhum acesso a fs/child_process
// é exposto ao renderer.
contextBridge.exposeInMainWorld("artifex", {
  backendUrl: "http://127.0.0.1:8000",
});
