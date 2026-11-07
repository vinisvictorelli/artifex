import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { DownloadTool } from "./DownloadTool";
import { api, type JobStatus, type VideoInfo } from "../lib/api";

vi.mock("../lib/api", () => ({
  api: {
    downloadInfo: vi.fn(),
    downloadStart: vi.fn(),
    downloadStatus: vi.fn(),
    downloadCancel: vi.fn(),
  },
}));

const info: VideoInfo = {
  title: "Vídeo de teste",
  duration: 125,
  qualities: [
    { height: 1080, fps: 60, label: "1080p60", size: 123_000_000 },
    { height: 720, fps: 30, label: "720p", size: null },
    { height: 360, fps: 30, label: "360p", size: 1_610_612_736 },
  ],
};

const doneJob: JobStatus = {
  job_id: "j1",
  status: "done",
  phase: "merging",
  downloaded: 1,
  total: 1,
  percent: 100,
  speed: null,
  eta: null,
  output_path: "/tmp/v.mp4",
  error: null,
};

const mocked = vi.mocked(api);
const URL_A = "https://youtu.be/aaa";
const DEBOUNCE = 600;

function urlInput() {
  return screen.getByPlaceholderText("https://...") as HTMLInputElement;
}

function typeUrl(value: string) {
  fireEvent.change(urlInput(), { target: { value } });
}

/** Avança o debounce e deixa as promises pendentes resolverem. */
async function settle(ms = DEBOUNCE) {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(ms);
  });
}

function qualitySelect() {
  return screen.queryByLabelText("Qualidade") as HTMLSelectElement | null;
}

function optionLabels(select: HTMLSelectElement) {
  return Array.from(select.options).map((o) => o.textContent);
}

beforeEach(() => {
  vi.useFakeTimers();
  vi.resetAllMocks();
  mocked.downloadInfo.mockResolvedValue(info);
  mocked.downloadStart.mockResolvedValue({ job_id: "j1" });
  mocked.downloadStatus.mockResolvedValue(doneJob);
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
});

describe("consulta de qualidades", () => {
  it("não consulta sem URL ou com URL que não é http(s)", async () => {
    render(<DownloadTool />);
    typeUrl("");
    await settle();
    typeUrl("youtube.com/watch?v=1");
    await settle();
    typeUrl("ftp://x/y");
    await settle();
    expect(mocked.downloadInfo).not.toHaveBeenCalled();
    expect(qualitySelect()).toBeNull();
  });

  it("espera o debounce e consulta uma única vez enquanto o usuário digita", async () => {
    render(<DownloadTool />);
    typeUrl("https://youtu.be/a");
    await settle(300);
    typeUrl("https://youtu.be/ab");
    await settle(300);
    expect(mocked.downloadInfo).not.toHaveBeenCalled();
    await settle(400);
    expect(mocked.downloadInfo).toHaveBeenCalledTimes(1);
    expect(mocked.downloadInfo).toHaveBeenCalledWith("https://youtu.be/ab");
  });

  it("ignora espaços ao redor da URL", async () => {
    render(<DownloadTool />);
    typeUrl(`  ${URL_A}  `);
    await settle();
    expect(mocked.downloadInfo).toHaveBeenCalledWith(URL_A);
  });

  it("mostra 'Buscando qualidades...' enquanto aguarda a resposta", async () => {
    mocked.downloadInfo.mockReturnValue(new Promise(() => {}));
    render(<DownloadTool />);
    typeUrl(URL_A);
    await settle();
    expect(screen.getByText("Buscando qualidades...")).toBeTruthy();
    expect(qualitySelect()).toBeNull();
  });

  it("mostra título e lista as qualidades reais, com tamanho quando conhecido", async () => {
    render(<DownloadTool />);
    typeUrl(URL_A);
    await settle();
    expect(screen.getByText("Vídeo de teste")).toBeTruthy();
    const select = qualitySelect()!;
    expect(optionLabels(select)).toEqual([
      "Melhor disponível",
      "1080p60 · ~117 MB",
      "720p",
      "360p · ~1.5 GB",
    ]);
    expect(select.value).toBe("best");
    expect(screen.queryByText("Buscando qualidades...")).toBeNull();
  });

  it("em caso de erro, mostra a mensagem e mantém o download na melhor qualidade", async () => {
    mocked.downloadInfo.mockRejectedValue(new Error("Falha — Video unavailable"));
    render(<DownloadTool />);
    typeUrl(URL_A);
    await settle();
    expect(screen.getByText(/Video unavailable.*melhor qualidade/)).toBeTruthy();
    expect(qualitySelect()).toBeNull();
    const button = screen.getByRole("button", { name: "Baixar" }) as HTMLButtonElement;
    expect(button.disabled).toBe(false);
  });

  it("o botão 'Buscar qualidades' repete a consulta que falhou", async () => {
    mocked.downloadInfo.mockRejectedValueOnce(new Error("Failed to fetch"));
    render(<DownloadTool />);
    typeUrl(URL_A);
    await settle();
    expect(qualitySelect()).toBeNull();
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Buscar qualidades" }));
      await vi.advanceTimersByTimeAsync(0);
    });
    expect(mocked.downloadInfo).toHaveBeenCalledTimes(2);
    expect(qualitySelect()).not.toBeNull();
    expect(screen.queryByRole("button", { name: "Buscar qualidades" })).toBeNull();
  });

  it("o botão só aparece com uma URL http(s) válida", async () => {
    render(<DownloadTool />);
    expect(screen.queryByRole("button", { name: "Buscar qualidades" })).toBeNull();
    typeUrl("não é url");
    expect(screen.queryByRole("button", { name: "Buscar qualidades" })).toBeNull();
    typeUrl(URL_A);
    expect(screen.getByRole("button", { name: "Buscar qualidades" })).toBeTruthy();
  });

  it("trocar a URL descarta qualidades e escolha anteriores", async () => {
    render(<DownloadTool />);
    typeUrl(URL_A);
    await settle();
    fireEvent.change(qualitySelect()!, { target: { value: "720" } });
    typeUrl("https://youtu.be/bbb");
    expect(qualitySelect()).toBeNull();
    expect(screen.queryByText("Vídeo de teste")).toBeNull();
    await settle();
    expect(qualitySelect()!.value).toBe("best");
  });

  it("limpar a URL volta ao estado inicial", async () => {
    render(<DownloadTool />);
    typeUrl(URL_A);
    await settle();
    typeUrl("");
    expect(qualitySelect()).toBeNull();
    expect(screen.queryByText("Vídeo de teste")).toBeNull();
  });

  it("descarta a resposta atrasada de uma URL antiga", async () => {
    let resolveOld!: (v: VideoInfo) => void;
    mocked.downloadInfo
      .mockReturnValueOnce(new Promise<VideoInfo>((r) => (resolveOld = r)))
      .mockResolvedValueOnce({ ...info, title: "Vídeo novo", qualities: [info.qualities[2]] });
    render(<DownloadTool />);
    typeUrl(URL_A);
    await settle();
    typeUrl("https://youtu.be/bbb");
    await settle();
    await act(async () => resolveOld({ ...info, title: "Vídeo antigo" }));
    expect(screen.getByText("Vídeo novo")).toBeTruthy();
    expect(screen.queryByText("Vídeo antigo")).toBeNull();
    expect(optionLabels(qualitySelect()!)).toEqual(["Melhor disponível", "360p · ~1.5 GB"]);
  });

  it("descarta também o erro atrasado de uma URL antiga", async () => {
    let rejectOld!: (e: Error) => void;
    mocked.downloadInfo
      .mockReturnValueOnce(new Promise<VideoInfo>((_, rej) => (rejectOld = rej)))
      .mockResolvedValueOnce(info);
    render(<DownloadTool />);
    typeUrl(URL_A);
    await settle();
    typeUrl("https://youtu.be/bbb");
    await settle();
    await act(async () => rejectOld(new Error("falha antiga")));
    expect(screen.queryByText(/falha antiga/)).toBeNull();
    expect(qualitySelect()).not.toBeNull();
  });
});

describe("formato de áudio", () => {
  it("esconde o seletor de qualidade para mp3 e m4a e o devolve para vídeo", async () => {
    render(<DownloadTool />);
    typeUrl(URL_A);
    await settle();
    const format = screen.getByLabelText("Formato de saída");
    for (const audio of ["mp3", "m4a"]) {
      fireEvent.change(format, { target: { value: audio } });
      expect(qualitySelect()).toBeNull();
    }
    fireEvent.change(format, { target: { value: "mkv" } });
    expect(qualitySelect()).not.toBeNull();
  });

  it("preserva a qualidade escolhida ao alternar para áudio e voltar", async () => {
    render(<DownloadTool />);
    typeUrl(URL_A);
    await settle();
    fireEvent.change(qualitySelect()!, { target: { value: "720" } });
    const format = screen.getByLabelText("Formato de saída");
    fireEvent.change(format, { target: { value: "mp3" } });
    fireEvent.change(format, { target: { value: "mp4" } });
    expect(qualitySelect()!.value).toBe("720");
  });
});

describe("início do download", () => {
  const dest = "./downloads/video.mp4";

  async function prepare() {
    render(<DownloadTool />);
    typeUrl(URL_A);
    await settle();
    fireEvent.change(screen.getByPlaceholderText(dest), { target: { value: dest } });
  }

  async function run() {
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Baixar" }));
      await vi.advanceTimersByTimeAsync(0);
    });
  }

  it("sem escolher qualidade, não envia height (melhor disponível)", async () => {
    await prepare();
    await run();
    expect(mocked.downloadStart).toHaveBeenCalledTimes(1);
    expect(mocked.downloadStart).toHaveBeenCalledWith({
      url: URL_A,
      dest,
      format: "mp4",
      height: undefined,
    });
  });

  it("envia a altura numérica da qualidade escolhida", async () => {
    await prepare();
    fireEvent.change(qualitySelect()!, { target: { value: "720" } });
    await run();
    expect(mocked.downloadStart).toHaveBeenCalledWith(
      expect.objectContaining({ url: URL_A, format: "mp4", height: 720 }),
    );
  });

  it("voltar para 'Melhor disponível' remove o height", async () => {
    await prepare();
    fireEvent.change(qualitySelect()!, { target: { value: "1080" } });
    fireEvent.change(qualitySelect()!, { target: { value: "best" } });
    await run();
    expect(mocked.downloadStart.mock.calls[0][0].height).toBeUndefined();
  });

  it("formato de áudio nunca envia height, mesmo com qualidade escolhida antes", async () => {
    await prepare();
    fireEvent.change(qualitySelect()!, { target: { value: "360" } });
    fireEvent.change(screen.getByLabelText("Formato de saída"), { target: { value: "mp3" } });
    await run();
    expect(mocked.downloadStart).toHaveBeenCalledWith(
      expect.objectContaining({ format: "mp3", height: undefined }),
    );
  });

  it("baixa normalmente (melhor qualidade) quando a consulta falhou", async () => {
    mocked.downloadInfo.mockRejectedValue(new Error("boom"));
    await prepare();
    await run();
    expect(mocked.downloadStart).toHaveBeenCalledWith(
      expect.objectContaining({ url: URL_A, height: undefined }),
    );
  });

  it("baixa sem consultar quando a URL ainda está no debounce", async () => {
    render(<DownloadTool />);
    typeUrl(URL_A);
    fireEvent.change(screen.getByPlaceholderText(dest), { target: { value: dest } });
    await run();
    expect(mocked.downloadStart).toHaveBeenCalledWith(
      expect.objectContaining({ url: URL_A, height: undefined }),
    );
  });
});
