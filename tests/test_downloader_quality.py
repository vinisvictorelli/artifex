"""Qualidade do download: consulta (-J) e seleção de formato, ponta a ponta com yt-dlp falso."""

import os
import unittest

from artifex_core.downloader.downloader import (
    DownloadError,
    download_file,
    get_video_info,
    parse_qualities,
)
from tests.fake_ytdlp import SAMPLE_INFO, FakeYtDlp


def selector(args: list[str]) -> str:
    return args[args.index("-f") + 1]


class FakeEnvTestCase(unittest.TestCase):
    def setUp(self):
        self.fake = FakeYtDlp()
        self.fake.install()
        self.addCleanup(self.fake.uninstall)
        self.dest = os.path.join(self.fake.dir, "out", "video.mp4")


class ParseSampleInfoTest(unittest.TestCase):
    """parse_qualities contra uma resposta completa e realista."""

    def setUp(self):
        self.qualities = parse_qualities(SAMPLE_INFO)

    def test_heights_unique_and_descending(self):
        self.assertEqual([q.height for q in self.qualities], [1080, 720, 360])

    def test_labels_show_fps_only_above_30(self):
        self.assertEqual([q.label for q in self.qualities], ["1080p60", "720p60", "360p"])

    def test_best_candidate_per_height_wins(self):
        # 720p: o de 60 fps (60MB) vence o de 30 fps (40MB), e soma o melhor áudio (opus 3MB).
        self.assertEqual(self.qualities[1].size, 63_000_000)

    def test_filesize_approx_is_used(self):
        self.assertEqual(self.qualities[0].size, 123_000_000)

    def test_combined_format_competes_without_double_counting_audio(self):
        # 360p: vídeo-só (30fps, tbr 300) vs combinado (30fps, tbr 500). O combinado vence e não soma áudio.
        self.assertEqual(self.qualities[2].size, 15_000_000)


class GetVideoInfoEndToEndTest(FakeEnvTestCase):
    def test_returns_title_duration_and_qualities(self):
        info = get_video_info("https://youtu.be/x")
        self.assertEqual(info.title, "Vídeo de teste")
        self.assertEqual(info.duration, 125)
        self.assertEqual([q.height for q in info.qualities], [1080, 720, 360])

    def test_query_never_downloads_and_ignores_playlists(self):
        get_video_info("https://youtu.be/x")
        (call,) = self.fake.calls()
        self.assertIn("-J", call)
        self.assertIn("--no-playlist", call)
        self.assertEqual(call[-1], "https://youtu.be/x")
        self.assertNotIn("-o", call)

    def test_ytdlp_failure_becomes_download_error(self):
        os.environ["FAKE_MODE"] = "fail"
        with self.assertRaisesRegex(DownloadError, "Video unavailable"):
            get_video_info("u")

    def test_video_without_formats_has_no_qualities(self):
        os.environ["FAKE_INFO"] = '{"title": "Só áudio", "formats": []}'
        self.assertEqual(get_video_info("u").qualities, [])

    def test_missing_title_and_duration_are_tolerated(self):
        os.environ["FAKE_INFO"] = "{}"
        info = get_video_info("u")
        self.assertEqual((info.title, info.duration, info.qualities), ("", None, []))


class DownloadSelectsRequestedQualityTest(FakeEnvTestCase):
    def test_default_downloads_best(self):
        download_file("u", self.dest, "mp4")
        (call,) = self.fake.download_calls()
        self.assertEqual(selector(call), "bv*+ba/b")

    def test_height_limits_both_video_and_fallback(self):
        download_file("u", self.dest, "mp4", height=720)
        (call,) = self.fake.download_calls()
        self.assertEqual(selector(call), "bv*[height<=720]+ba/b[height<=720]")

    def test_size_probe_uses_the_same_selector(self):
        download_file("u", self.dest, "mp4", height=480)
        probes = [c for c in self.fake.calls() if "--simulate" in c]
        self.assertEqual(selector(probes[0]), "bv*[height<=480]+ba/b[height<=480]")

    def test_height_applies_to_every_video_container(self):
        for fmt in ("mp4", "mkv", "webm"):
            with self.subTest(fmt=fmt):
                open(self.fake.argv_log, "w").close()
                download_file("u", os.path.join(self.fake.dir, f"v.{fmt}"), fmt, height=1080)
                (call,) = self.fake.download_calls()
                self.assertEqual(call[call.index("--merge-output-format") + 1], fmt)
                self.assertIn("height<=1080", selector(call))

    def test_audio_formats_ignore_height(self):
        for fmt in ("mp3", "m4a"):
            with self.subTest(fmt=fmt):
                open(self.fake.argv_log, "w").close()
                download_file("u", os.path.join(self.fake.dir, f"a.{fmt}"), fmt, height=720)
                (call,) = self.fake.download_calls()
                self.assertIn("-x", call)
                self.assertNotIn("-f", call)

    def test_file_is_still_produced_with_height(self):
        self.assertEqual(download_file("u", self.dest, "mp4", height=360), self.dest)
        self.assertTrue(os.path.exists(self.dest))


if __name__ == "__main__":
    unittest.main()
