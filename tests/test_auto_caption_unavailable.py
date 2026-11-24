"""Sem Whisper instalado (ex.: build para Mac Intel), a legenda automática responde 501."""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "apps", "backend"))

try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
except ImportError:  # pragma: no cover
    FastAPI = None

from artifex_core.auto_caption.auto_caption import WhisperUnavailable, mp3_to_srt


class WhisperUnavailableTest(unittest.TestCase):
    def test_core_raises_clear_error(self):
        with mock.patch.dict(sys.modules, {"whisper": None}):  # força ImportError
            with self.assertRaises(WhisperUnavailable):
                mp3_to_srt("a.mp3", "a.srt")

    @unittest.skipIf(FastAPI is None, "fastapi/httpx não instalados")
    def test_api_returns_501_with_message(self):
        from app.routers import auto_caption

        app = FastAPI()
        app.include_router(auto_caption.router)
        with mock.patch.dict(sys.modules, {"whisper": None}):
            r = TestClient(app).post("/auto-caption", json={"audio_path": "a.mp3", "output_path": "a.srt"})
        self.assertEqual(r.status_code, 501)
        self.assertIn("sem Whisper", r.json()["detail"])


if __name__ == "__main__":
    unittest.main()
