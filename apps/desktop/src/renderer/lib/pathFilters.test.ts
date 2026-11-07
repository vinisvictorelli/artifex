import { describe, expect, it } from "vitest";
import { DOWNLOAD_FORMATS, isAudioDownloadFormat } from "./pathFilters";

describe("isAudioDownloadFormat", () => {
  it("identifica os formatos de áudio do download", () => {
    expect(isAudioDownloadFormat("mp3")).toBe(true);
    expect(isAudioDownloadFormat("m4a")).toBe(true);
  });

  it("trata os containers de vídeo como vídeo", () => {
    for (const f of ["mp4", "mkv", "webm"]) expect(isAudioDownloadFormat(f)).toBe(false);
  });

  it("cobre todas as opções 'somente áudio' oferecidas na UI", () => {
    const audioOptions = DOWNLOAD_FORMATS.filter((o) => o.label.includes("somente áudio"));
    expect(audioOptions.length).toBeGreaterThan(0);
    for (const o of audioOptions) expect(isAudioDownloadFormat(o.value)).toBe(true);
    for (const o of DOWNLOAD_FORMATS.filter((o) => !o.label.includes("somente áudio")))
      expect(isAudioDownloadFormat(o.value)).toBe(false);
  });
});
