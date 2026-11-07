"""yt-dlp falso, usado pelos testes de qualidade e da API.

Comportamento controlado por variáveis de ambiente:
    FAKE_ARGV_LOG   arquivo onde cada chamada anexa seus argumentos (JSON por linha)
    FAKE_INFO       JSON devolvido por `-J`
    FAKE_MODE       ok | fail | slow
"""

import json
import os
import stat
import sys
import tempfile

SCRIPT = f"""#!{sys.executable}
import json, os, sys, time
args = sys.argv[1:]
log = os.environ.get("FAKE_ARGV_LOG")
if log:
    with open(log, "a") as f:
        f.write(json.dumps(args) + "\\n")
mode = os.environ.get("FAKE_MODE", "ok")
if "-J" in args:
    if mode == "fail":
        print("ERROR: [youtube] x: Video unavailable", file=sys.stderr)
        sys.exit(1)
    print(os.environ.get("FAKE_INFO", "{{}}"))
    sys.exit(0)
if "--simulate" in args:
    print("1000")
    sys.exit(0)
dest = args[args.index("-o") + 1]
root, ext = os.path.splitext(dest)
if mode == "fail":
    print("ERROR: [youtube] x: This video is unavailable", flush=True)
    sys.exit(1)
print("[info] x: Downloading 1 format(s): 399+251", flush=True)
for part, fid in enumerate(["399", "251"], start=1):
    partial = f"{{root}}.f{{fid}}{{ext}}.part"
    open(partial, "w").write("x")
    print(f"[download] Destination: {{root}}.f{{fid}}{{ext}}", flush=True)
    for i in range(1, 5):
        done = 250 if part == 1 else 100
        print(f"ARTIFEX {{done * i // 4}} {{done}} NA 100.0 3", flush=True)
        if mode == "slow":
            time.sleep(0.3)
    if mode != "slow":
        os.remove(partial)
if mode == "slow":
    time.sleep(30)
print("[Merger] Merging formats", flush=True)
open(dest, "w").write("video")
"""

# Resposta realista de `yt-dlp -J`: duas resoluções de vídeo (uma delas com
# 60 fps duplicada em bitrate menor), dois áudios e um formato combinado.
SAMPLE_INFO = {
    "title": "Vídeo de teste",
    "duration": 125.4,
    "formats": [
        {"format_id": "140", "vcodec": "none", "acodec": "mp4a", "abr": 128, "filesize": 2_000_000},
        {"format_id": "251", "vcodec": "none", "acodec": "opus", "abr": 160, "filesize": 3_000_000},
        {"format_id": "134", "vcodec": "avc1", "acodec": "none", "height": 360, "fps": 30, "tbr": 300, "filesize": 10_000_000},
        {"format_id": "136", "vcodec": "avc1", "acodec": "none", "height": 720, "fps": 30, "tbr": 1000, "filesize": 40_000_000},
        {"format_id": "298", "vcodec": "avc1", "acodec": "none", "height": 720, "fps": 60, "tbr": 1800, "filesize": 60_000_000},
        {"format_id": "299", "vcodec": "avc1", "acodec": "none", "height": 1080, "fps": 60, "tbr": 3000, "filesize_approx": 120_000_000},
        {"format_id": "18", "vcodec": "avc1", "acodec": "mp4a", "height": 360, "fps": 30, "tbr": 500, "filesize": 15_000_000},
    ],
}


class FakeYtDlp:
    """Instala o yt-dlp falso no PATH durante um teste (setUp/tearDown)."""

    def install(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        bin_dir = os.path.join(self.dir, "bin")
        os.makedirs(bin_dir)
        fake = os.path.join(bin_dir, "yt-dlp")
        with open(fake, "w") as f:
            f.write(SCRIPT)
        os.chmod(fake, os.stat(fake).st_mode | stat.S_IEXEC)
        self._old_path = os.environ["PATH"]
        os.environ["PATH"] = bin_dir + os.pathsep + self._old_path
        self.argv_log = os.path.join(self.dir, "argv.log")
        os.environ["FAKE_ARGV_LOG"] = self.argv_log
        os.environ["FAKE_INFO"] = json.dumps(SAMPLE_INFO)

    def uninstall(self) -> None:
        os.environ["PATH"] = self._old_path
        for key in ("FAKE_ARGV_LOG", "FAKE_INFO", "FAKE_MODE"):
            os.environ.pop(key, None)
        self._tmp.cleanup()

    def calls(self) -> list[list[str]]:
        if not os.path.exists(self.argv_log):
            return []
        with open(self.argv_log) as f:
            return [json.loads(line) for line in f if line.strip()]

    def download_calls(self) -> list[list[str]]:
        """Chamadas de download real (exclui -J e --simulate)."""
        return [c for c in self.calls() if "-J" not in c and "--simulate" not in c]
