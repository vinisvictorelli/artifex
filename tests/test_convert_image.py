import os
import tempfile
import unittest

from PIL import Image

from artifex_core.convert_image.convert_image import convert_image


class ConvertImageTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _path(self, name):
        return os.path.join(self.dir, name)

    def test_png_with_alpha_to_jpeg_flattens_on_white(self):
        src = self._path("a.png")
        Image.new("RGBA", (4, 4), (255, 0, 0, 0)).save(src)
        out = convert_image(src, self._path("a.jpg"), "jpg")
        with Image.open(out) as img:
            self.assertEqual(img.format, "JPEG")
            r, g, b = img.getpixel((1, 1))
            self.assertGreater(min(r, g, b), 240)

    def test_png_to_every_format(self):
        src = self._path("a.png")
        Image.new("RGBA", (8, 8), (0, 128, 255, 200)).save(src)
        for ext in ["jpg", "gif", "webp", "avif", "bmp", "tiff", "ico", "tga", "pdf"]:
            out = convert_image(src, self._path(f"out.{ext}"), ext)
            self.assertGreater(os.path.getsize(out), 0, ext)

    def test_gif_to_png(self):
        src = self._path("a.gif")
        Image.new("P", (4, 4)).save(src)
        out = convert_image(src, self._path("a.png"), "png")
        with Image.open(out) as img:
            self.assertEqual(img.format, "PNG")

    def test_animated_gif_to_webp_keeps_frames(self):
        src = self._path("anim.gif")
        frames = [Image.new("RGB", (4, 4), c) for c in [(255, 0, 0), (0, 255, 0), (0, 0, 255)]]
        frames[0].save(src, save_all=True, append_images=frames[1:], duration=50, loop=0)
        out = convert_image(src, self._path("anim.webp"), "webp")
        with Image.open(out) as img:
            self.assertEqual(img.n_frames, 3)

    def test_animated_gif_to_png_uses_first_frame(self):
        src = self._path("anim.gif")
        frames = [Image.new("RGB", (4, 4), c) for c in [(255, 0, 0), (0, 255, 0)]]
        frames[0].save(src, save_all=True, append_images=frames[1:])
        out = convert_image(src, self._path("f.png"), "png")
        with Image.open(out) as img:
            self.assertEqual(img.format, "PNG")

    def test_ico_is_capped_to_256(self):
        src = self._path("big.png")
        Image.new("RGB", (600, 400)).save(src)
        out = convert_image(src, self._path("big.ico"), "ico")
        with Image.open(out) as img:
            self.assertLessEqual(max(img.size), 256)

    def test_default_output_is_temp_file(self):
        src = self._path("a.png")
        Image.new("RGB", (4, 4)).save(src)
        out = convert_image(src, None, "webp")
        self.addCleanup(os.remove, out)
        self.assertTrue(out.endswith(".webp"))

    def test_unsupported_format(self):
        src = self._path("a.png")
        Image.new("RGB", (4, 4)).save(src)
        with self.assertRaises(ValueError):
            convert_image(src, None, "heic")

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            convert_image(self._path("nope.png"), None, "jpg")


if __name__ == "__main__":
    unittest.main()
