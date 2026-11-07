"""API do downloader (/downloader/info e /downloader), com yt-dlp falso.

Requer fastapi e httpx. Monta um app só com o router do downloader para não
importar os demais (torch, whisper, moviepy).
"""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "apps", "backend"))

try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
except ImportError:  # pragma: no cover
    FastAPI = None

from tests.fake_ytdlp import FakeYtDlp


def wait_for(client, job_id, timeout=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        data = client.get(f"/downloader/{job_id}").json()
        if data["status"] != "running":
            return data
        time.sleep(0.05)
    raise AssertionError("job não terminou a tempo")


@unittest.skipIf(FastAPI is None, "fastapi/httpx não instalados")
class DownloaderApiTest(unittest.TestCase):
    def setUp(self):
        from app.routers import downloader

        app = FastAPI()
        app.include_router(downloader.router)
        self.client = TestClient(app)
        self.fake = FakeYtDlp()
        self.fake.install()
        self.addCleanup(self.fake.uninstall)
        self.dest = os.path.join(self.fake.dir, "out", "video.mp4")

    # --- /downloader/info ---------------------------------------------------

    def test_info_returns_title_duration_and_qualities(self):
        r = self.client.post("/downloader/info", json={"url": "https://youtu.be/x"})
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["title"], "Vídeo de teste")
        self.assertEqual(body["duration"], 125)
        self.assertEqual([q["height"] for q in body["qualities"]], [1080, 720, 360])
        self.assertEqual(set(body["qualities"][0]), {"height", "fps", "label", "size"})
        self.assertEqual(body["qualities"][0]["label"], "1080p60")

    def test_info_is_not_captured_by_job_id_route(self):
        # /info é POST; /{job_id} só tem GET/DELETE. Um GET em /info cai no job inexistente.
        self.assertEqual(self.client.get("/downloader/info").status_code, 404)
        self.assertEqual(self.client.post("/downloader/info", json={"url": "u"}).status_code, 200)

    def test_info_failure_is_422_with_ytdlp_message(self):
        os.environ["FAKE_MODE"] = "fail"
        r = self.client.post("/downloader/info", json={"url": "u"})
        self.assertEqual(r.status_code, 422)
        self.assertIn("Video unavailable", r.json()["detail"])

    def test_info_requires_url(self):
        self.assertEqual(self.client.post("/downloader/info", json={}).status_code, 422)

    def test_info_does_not_create_jobs_or_files(self):
        self.client.post("/downloader/info", json={"url": "u"})
        self.assertEqual(self.fake.download_calls(), [])
        self.assertFalse(os.path.exists(os.path.dirname(self.dest)))

    # --- POST /downloader com height -----------------------------------------

    def _start(self, **extra):
        payload = {"url": "u", "dest": self.dest, **extra}
        r = self.client.post("/downloader", json=payload)
        self.assertEqual(r.status_code, 200, r.text)
        return wait_for(self.client, r.json()["job_id"])

    def test_download_without_height_is_best(self):
        job = self._start()
        self.assertEqual(job["status"], "done")
        (call,) = self.fake.download_calls()
        self.assertEqual(call[call.index("-f") + 1], "bv*+ba/b")

    def test_download_with_height_reaches_ytdlp(self):
        job = self._start(height=720)
        self.assertEqual(job["status"], "done")
        self.assertEqual(job["output_path"], self.dest)
        self.assertTrue(os.path.exists(self.dest))
        (call,) = self.fake.download_calls()
        self.assertEqual(call[call.index("-f") + 1], "bv*[height<=720]+ba/b[height<=720]")

    def test_null_height_is_accepted_as_best(self):
        self._start(height=None)
        (call,) = self.fake.download_calls()
        self.assertEqual(call[call.index("-f") + 1], "bv*+ba/b")

    def test_invalid_height_is_rejected_before_starting(self):
        for bad in (0, -1, "abc", 7.5):
            with self.subTest(height=bad):
                r = self.client.post("/downloader", json={"url": "u", "dest": self.dest, "height": bad})
                self.assertEqual(r.status_code, 422)
        self.assertEqual(self.fake.calls(), [])

    def test_audio_download_ignores_height(self):
        job = self._start(format="mp3", dest=os.path.join(self.fake.dir, "a.mp3"), height=720)
        self.assertEqual(job["status"], "done")
        (call,) = self.fake.download_calls()
        self.assertNotIn("-f", call)

    def test_download_failure_reports_error_job(self):
        os.environ["FAKE_MODE"] = "fail"
        job = self._start(height=720)
        self.assertEqual(job["status"], "error")
        self.assertIn("This video is unavailable", job["error"])

    def test_progress_reaches_100_percent_when_done(self):
        job = self._start(height=360)
        self.assertEqual(job["percent"], 100.0)

    # --- status / cancelamento ------------------------------------------------

    def test_unknown_job_is_404(self):
        self.assertEqual(self.client.get("/downloader/nope").status_code, 404)
        self.assertEqual(self.client.delete("/downloader/nope").status_code, 404)

    def test_cancel_stops_job_with_height(self):
        os.environ["FAKE_MODE"] = "slow"
        r = self.client.post("/downloader", json={"url": "u", "dest": self.dest, "height": 1080})
        job_id = r.json()["job_id"]
        time.sleep(0.8)
        self.assertEqual(self.client.delete(f"/downloader/{job_id}").status_code, 200)
        self.assertEqual(wait_for(self.client, job_id)["status"], "cancelled")
        leftovers = [f for f in os.listdir(os.path.dirname(self.dest)) if ".part" in f or ".f" in f]
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
