const BASE_URL = window.artifex?.backendUrl ?? "http://127.0.0.1:8000";

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = "";
    try {
      const data = await res.json();
      if (typeof data?.detail === "string") detail = ` — ${data.detail}`;
    } catch {
      // corpo sem JSON: mantém só o status
    }
    throw new Error(`Falha na requisição ${path}: ${res.status}${detail}`);
  }
  return res.json();
}

async function request<T>(method: "GET" | "DELETE", path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { method });
  if (!res.ok) {
    throw new Error(`Falha na requisição ${path}: ${res.status}`);
  }
  return res.json();
}

export type JobStatus = {
  job_id: string;
  status: "running" | "done" | "error" | "cancelled";
  phase: "preparing" | "video" | "audio" | "download" | "merging";
  downloaded: number;
  total: number | null;
  percent: number | null;
  speed: number | null;
  eta: number | null;
  output_path: string | null;
  error: string | null;
};

export const api = {
  autoCaption: (payload: { audio_path: string; output_path: string }) =>
    post<{ output_path: string }>("/auto-caption", payload),

  extractAudio: (payload: { video_path: string; output_path?: string; format?: string }) =>
    post<{ output_path: string }>("/extract-audio", payload),

  convertImage: (payload: {
    image_path: string;
    output_path?: string;
    format?: string;
    quality?: number;
  }) => post<{ output_path: string }>("/convert-image", payload),

  autoCut: (payload: { video_path: string; output_path: string; format?: string }) =>
    post<{ output_path: string }>("/cutting-tool/auto-cut", payload),

  downloadStart: (payload: { url: string; dest: string; format?: string }) =>
    post<{ job_id: string }>("/downloader", payload),

  downloadStatus: (jobId: string) => request<JobStatus>("GET", `/downloader/${jobId}`),

  downloadCancel: (jobId: string) => request<JobStatus>("DELETE", `/downloader/${jobId}`),
};
