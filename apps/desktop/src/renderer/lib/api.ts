const BASE_URL = window.artifex?.backendUrl ?? "http://127.0.0.1:8000";

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`Falha na requisição ${path}: ${res.status}`);
  }
  return res.json();
}

export const api = {
  autoCaption: (payload: { audio_path: string; output_path: string }) =>
    post<{ output_path: string }>("/auto-caption", payload),

  extractAudio: (payload: { video_path: string; output_path?: string; format?: string }) =>
    post<{ output_path: string }>("/extract-audio", payload),

  autoCut: (payload: { video_path: string; output_path: string; format?: string }) =>
    post<{ output_path: string }>("/cutting-tool/auto-cut", payload),

  download: (payload: { url: string; dest: string; format?: string }) =>
    post<{ output_path: string }>("/downloader", payload),
};
