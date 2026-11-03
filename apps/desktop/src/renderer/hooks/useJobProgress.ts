import { useCallback, useEffect, useRef, useState } from "react";
import type { JobStatus } from "../lib/api";

const POLL_INTERVAL_MS = 500;

// Jobs em andamento por ferramenta. Vive fora do componente porque só a aba
// ativa fica montada: ao voltar para ela, retomamos o acompanhamento.
const running = new Map<string, string>();

type Api = {
  status: (jobId: string) => Promise<JobStatus>;
  cancel: (jobId: string) => Promise<JobStatus>;
};

export function useJobProgress(key: string, api: Api) {
  const [job, setJob] = useState<JobStatus | null>(null);
  const [active, setActive] = useState(() => running.has(key));
  const alive = useRef(true);
  const apiRef = useRef(api);
  apiRef.current = api;

  const track = useCallback(
    async (jobId: string): Promise<JobStatus> => {
      running.set(key, jobId);
      setActive(true);
      for (;;) {
        let current: JobStatus;
        try {
          current = await apiRef.current.status(jobId);
        } catch (err) {
          running.delete(key);
          setActive(false);
          throw err;
        }
        // Desmontado: o job segue no backend e é retomado ao voltar para a aba.
        if (!alive.current) throw new Error("abandoned");

        setJob(current);
        if (current.status !== "running") {
          running.delete(key);
          setActive(false);
          if (current.status === "error") throw new Error(current.error ?? "Erro desconhecido");
          if (current.status === "cancelled") throw new Error("Download cancelado");
          return current;
        }
        await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
        if (!alive.current) throw new Error("abandoned");
      }
    },
    [key],
  );

  useEffect(() => {
    alive.current = true;
    const resumeId = running.get(key);
    if (resumeId) track(resumeId).catch(() => {});
    return () => {
      alive.current = false;
    };
  }, [key, track]);

  const cancel = useCallback(async () => {
    const jobId = running.get(key);
    if (jobId) await apiRef.current.cancel(jobId).catch(() => {});
  }, [key]);

  return { job, active, track, cancel };
}
