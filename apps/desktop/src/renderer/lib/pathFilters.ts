import type { PathFilter } from "../components/PathInput";

const ALL: PathFilter = { name: "Todos os arquivos", extensions: ["*"] };

export const VIDEO_FILTERS: PathFilter[] = [
  { name: "Vídeo", extensions: ["mp4", "mov", "mkv", "webm", "avi"] },
  ALL,
];

export const AUDIO_FILTERS: PathFilter[] = [
  { name: "Áudio", extensions: ["wav", "mp3", "m4a", "ogg", "opus", "flac", "aac"] },
  ALL,
];

export const SRT_FILTERS: PathFilter[] = [{ name: "Legenda SRT", extensions: ["srt"] }, ALL];

// --- Formatos de saída (seletor de formato) ---------------------------------

export type FormatOption = { value: string; label: string };

export const DOWNLOAD_FORMATS: FormatOption[] = [
  { value: "mp4", label: "MP4 (vídeo)" },
  { value: "mkv", label: "MKV (vídeo)" },
  { value: "webm", label: "WebM (vídeo)" },
  { value: "mp3", label: "MP3 (somente áudio)" },
  { value: "m4a", label: "M4A (somente áudio)" },
];

export const EXTRACT_AUDIO_FORMATS: FormatOption[] = [
  { value: "wav", label: "WAV" },
  { value: "mp3", label: "MP3" },
  { value: "aac", label: "AAC" },
  { value: "flac", label: "FLAC" },
  { value: "ogg", label: "OGG" },
];

export const AUTO_CUT_FORMATS: FormatOption[] = [
  { value: "mp4", label: "MP4" },
  { value: "mkv", label: "MKV" },
  { value: "mov", label: "MOV" },
  { value: "webm", label: "WebM" },
];

/** Filtro do explorador para o formato escolhido (com "todos os arquivos" ao final). */
export function filtersForFormat(format: string): PathFilter[] {
  return [{ name: format.toUpperCase(), extensions: [format] }, ALL];
}

/** Troca apenas a extensão final do nome do arquivo, preservando o diretório. */
export function swapExtension(path: string, ext: string): string {
  if (!path) return path;
  const slash = Math.max(path.lastIndexOf("/"), path.lastIndexOf("\\"));
  const dir = path.slice(0, slash + 1);
  const name = path.slice(slash + 1);
  const dot = name.lastIndexOf(".");
  const base = dot > 0 ? name.slice(0, dot) : name;
  return `${dir}${base}.${ext}`;
}
