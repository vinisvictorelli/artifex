import {
  app,
  BrowserWindow,
  dialog,
  ipcMain,
  type OpenDialogOptions,
  type SaveDialogOptions,
} from "electron";
import { spawn, ChildProcess } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const isDev = process.env.NODE_ENV === "development";

let backendProcess: ChildProcess | null = null;
let mainWindow: BrowserWindow | null = null;

type DialogFilter = { name: string; extensions: string[] };
type OpenFilePayload = { title?: string; filters?: DialogFilter[]; defaultPath?: string };
type OpenDirectoryPayload = { title?: string; defaultPath?: string };
type SaveFilePayload = { title?: string; filters?: DialogFilter[]; defaultPath?: string };

function ownerWindow(): BrowserWindow | null {
  return BrowserWindow.getFocusedWindow() ?? mainWindow;
}

// Diálogos nativos do SO. Só existem no processo main; o renderer os
// aciona por IPC (ver preload). A API é estreita de propósito: o main
// decide os tipos de diálogo permitidos, o renderer nunca toca em fs.
function registerDialogHandlers() {
  ipcMain.handle("dialog:openFile", async (_event, payload: OpenFilePayload = {}) => {
    const options: OpenDialogOptions = {
      title: payload.title,
      defaultPath: payload.defaultPath || undefined,
      filters: payload.filters,
      properties: ["openFile"],
    };
    const win = ownerWindow();
    const result = win
      ? await dialog.showOpenDialog(win, options)
      : await dialog.showOpenDialog(options);
    return result.canceled || result.filePaths.length === 0 ? null : result.filePaths[0];
  });

  ipcMain.handle("dialog:openDirectory", async (_event, payload: OpenDirectoryPayload = {}) => {
    const options: OpenDialogOptions = {
      title: payload.title,
      defaultPath: payload.defaultPath || undefined,
      properties: ["openDirectory", "createDirectory"],
    };
    const win = ownerWindow();
    const result = win
      ? await dialog.showOpenDialog(win, options)
      : await dialog.showOpenDialog(options);
    return result.canceled || result.filePaths.length === 0 ? null : result.filePaths[0];
  });

  ipcMain.handle("dialog:saveFile", async (_event, payload: SaveFilePayload = {}) => {
    const options: SaveDialogOptions = {
      title: payload.title,
      defaultPath: payload.defaultPath || undefined,
      filters: payload.filters,
      properties: ["createDirectory", "showOverwriteConfirmation"],
    };
    const win = ownerWindow();
    const result = win
      ? await dialog.showSaveDialog(win, options)
      : await dialog.showSaveDialog(options);
    return result.canceled || !result.filePath ? null : result.filePath;
  });
}

function startBackend() {
  // Em dev, o backend roda separadamente (poetry run uvicorn app.main:app).
  // Em produção, o Electron sobe o backend empacotado (PyInstaller) via resourcesPath.
  if (isDev) return;

  const backendBin = path.join(process.resourcesPath, "backend", "artifex-backend");
  backendProcess = spawn(backendBin, [], { stdio: "inherit" });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: "#0f0f12",
    titleBarStyle: "hiddenInset",
    webPreferences: {
      preload: path.join(__dirname, "../preload/index.js"),
      contextIsolation: true,
      nodeIntegration: false,
      // Preload precisa de ipcRenderer (ponte de diálogos). Isolamento de
      // contexto e nodeIntegration desligado seguem valendo — o renderer
      // continua sem acesso direto a Node/fs.
      sandbox: false,
    },
  });

  if (isDev) {
    mainWindow.loadURL("http://localhost:5173");
    mainWindow.webContents.openDevTools({ mode: "detach" });
  } else {
    mainWindow.loadFile(path.join(__dirname, "../../dist-renderer/index.html"));
  }

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  registerDialogHandlers();
  startBackend();
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  backendProcess?.kill();
  if (process.platform !== "darwin") app.quit();
});

app.on("before-quit", () => {
  backendProcess?.kill();
});
