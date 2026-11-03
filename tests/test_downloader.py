import os
import stat
import sys
import tempfile
import threading
import unittest

from artifex_core.downloader.downloader import (
    DownloadCancelled,
    DownloadError,
    Progress,
    download_file,
    parse_progress_line,
)

FAKE_YTDLP = f"""#!{sys.executable}
import os, sys, time
args = sys.argv[1:]
if "--simulate" in args:
    print("1000")
    sys.exit(0)
dest = args[args.index("-o") + 1]
root, ext = os.path.splitext(dest)
mode = os.environ.get("FAKE_MODE", "ok")
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
    os.remove(partial) if mode != "slow" else None
if mode == "slow":
    time.sleep(30)
print("[Merger] Merging formats", flush=True)
open(dest, "w").write("video")
"""


class ParseProgressTest(unittest.TestCase):
    def test_exact_total(self):
        self.assertEqual(parse_progress_line("ARTIFEX 100 400 NA 50.5 8"), (100, 400, 50.5, 8))

    def test_estimated_total(self):
        self.assertEqual(parse_progress_line("ARTIFEX 100 NA 500 NA NA"), (100, 500, None, None))

    def test_unknown_total(self):
        self.assertEqual(parse_progress_line("ARTIFEX 100 NA NA 10.0 NA"), (100, None, 10.0, None))

    def test_ignores_other_lines(self):
        self.assertIsNone(parse_progress_line("[download] Destination: x.mp4"))
        self.assertIsNone(parse_progress_line(""))


class DownloadFileTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        bin_dir = os.path.join(self.dir, "bin")
        os.makedirs(bin_dir)
        fake = os.path.join(bin_dir, "yt-dlp")
        with open(fake, "w") as f:
            f.write(FAKE_YTDLP)
        os.chmod(fake, os.stat(fake).st_mode | stat.S_IEXEC)
        self._old_path = os.environ["PATH"]
        os.environ["PATH"] = bin_dir + os.pathsep + self._old_path
        self.dest = os.path.join(self.dir, "out", "video.mp4")

    def tearDown(self):
        os.environ["PATH"] = self._old_path
        os.environ.pop("FAKE_MODE", None)
        self._tmp.cleanup()

    def test_progress_is_monotonic_and_uses_expected_total(self):
        seen: list[Progress] = []
        out = download_file("u", self.dest, "mp4", lambda p: seen.append(Progress(**vars(p))))
        self.assertEqual(out, self.dest)
        self.assertTrue(os.path.exists(self.dest))
        self.assertEqual(seen[-1].phase, "merging")
        downloads = [p.downloaded for p in seen]
        self.assertEqual(downloads, sorted(downloads))
        self.assertTrue(all(p.total == 1000 for p in seen if p.phase in ("video", "audio")))
        self.assertEqual({"preparing", "video", "audio", "merging"}, {p.phase for p in seen})

    def test_error_carries_ytdlp_message(self):
        os.environ["FAKE_MODE"] = "fail"
        with self.assertRaises(DownloadError) as ctx:
            download_file("u", self.dest, "mp4")
        self.assertIn("This video is unavailable", str(ctx.exception))

    def test_cancel_stops_and_removes_partials(self):
        os.environ["FAKE_MODE"] = "slow"
        cancel = threading.Event()
        threading.Timer(0.8, cancel.set).start()
        with self.assertRaises(DownloadCancelled):
            download_file("u", self.dest, "mp4", cancel_event=cancel)
        leftovers = [f for f in os.listdir(os.path.dirname(self.dest)) if ".part" in f or ".f" in f]
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
