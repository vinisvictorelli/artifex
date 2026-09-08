/// <reference types="vite/client" />

type ArtifexDialogFilter = { name: string; extensions: string[] };

interface Window {
  artifex: {
    backendUrl: string;
    openFile?: (opts?: {
      title?: string;
      filters?: ArtifexDialogFilter[];
      defaultPath?: string;
    }) => Promise<string | null>;
    openDirectory?: (opts?: {
      title?: string;
      defaultPath?: string;
    }) => Promise<string | null>;
    saveFile?: (opts?: {
      title?: string;
      filters?: ArtifexDialogFilter[];
      defaultPath?: string;
    }) => Promise<string | null>;
  };
}
