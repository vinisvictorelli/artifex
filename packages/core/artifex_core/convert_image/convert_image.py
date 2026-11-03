import os
import tempfile

from PIL import Image, ImageOps

# Formato do Pillow por extensão de saída.
_PILLOW_FORMAT_BY_EXT = {
    "png": "PNG",
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "gif": "GIF",
    "webp": "WEBP",
    "bmp": "BMP",
    "tiff": "TIFF",
    "tif": "TIFF",
    "ico": "ICO",
    "tga": "TGA",
    "pdf": "PDF",
    "avif": "AVIF",
}

# Formatos que aceitam o parâmetro de qualidade.
_QUALITY_FORMATS = {"JPEG", "WEBP", "AVIF"}
# Formatos sem canal alfa: transparência é composta sobre fundo branco.
_NO_ALPHA_FORMATS = {"JPEG", "BMP", "PDF"}
# Formatos que suportam animação (múltiplos frames).
_ANIMATED_FORMATS = {"GIF", "WEBP"}
_ICO_MAX_SIZE = 256


def _has_alpha(img: Image.Image) -> bool:
    return img.mode in ("RGBA", "LA", "PA") or "transparency" in img.info


def _flatten(img: Image.Image) -> Image.Image:
    """Compõe a imagem sobre fundo branco, descartando a transparência."""
    rgba = img.convert("RGBA")
    background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    return Image.alpha_composite(background, rgba).convert("RGB")


def _prepare(img: Image.Image, pillow_format: str) -> Image.Image:
    if pillow_format in _NO_ALPHA_FORMATS:
        return _flatten(img) if _has_alpha(img) else img.convert("RGB")
    if pillow_format == "GIF":
        return img.convert("RGBA") if _has_alpha(img) else img.convert("RGB")
    if pillow_format == "TGA" and img.mode not in ("RGB", "RGBA", "L"):
        return img.convert("RGBA" if _has_alpha(img) else "RGB")
    if img.mode in ("CMYK", "YCbCr", "LAB", "HSV", "I;16", "P", "PA"):
        return img.convert("RGBA" if _has_alpha(img) else "RGB")
    return img


def convert_image(
    image_path: str,
    output_path: str | None = None,
    format: str = "png",
    quality: int = 90,
) -> str:
    """
    Converte uma imagem para outro formato.

    Args:
        image_path: Caminho da imagem de entrada.
        output_path: Caminho de saída. Se não informado, usa um arquivo
            temporário do sistema com a extensão do formato.
        format: Formato de saída (png, jpg, gif, webp, bmp, tiff, ico, tga,
            pdf, avif).
        quality: Qualidade de 1 a 100, usada apenas em JPEG, WebP e AVIF.

    Returns:
        Caminho da imagem gerada.
    """
    ext = format.lower().lstrip(".")
    pillow_format = _PILLOW_FORMAT_BY_EXT.get(ext)
    if pillow_format is None:
        raise ValueError(f"Formato de saída não suportado: {format}")
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix=f".{ext}", prefix="artifex_image_")
        os.close(fd)
    else:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    save_kwargs: dict = {}
    if pillow_format in _QUALITY_FORMATS:
        save_kwargs["quality"] = max(1, min(100, quality))

    with Image.open(image_path) as src:
        n_frames = getattr(src, "n_frames", 1)
        animated = n_frames > 1 and pillow_format in _ANIMATED_FORMATS

        if animated:
            # Preserva a animação (ex.: GIF -> WebP), mantendo duração e loop.
            frames, durations = [], []
            for i in range(n_frames):
                src.seek(i)
                frames.append(_prepare(ImageOps.exif_transpose(src.copy()), pillow_format))
                durations.append(src.info.get("duration", 100))
            save_kwargs.update(
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=src.info.get("loop", 0),
            )
            img = frames[0]
        else:
            # Formatos estáticos usam apenas o primeiro frame.
            src.seek(0)
            img = _prepare(ImageOps.exif_transpose(src.copy()), pillow_format)

        if pillow_format == "ICO":
            img.thumbnail((_ICO_MAX_SIZE, _ICO_MAX_SIZE))
        if pillow_format in ("PNG", "WEBP", "AVIF", "TIFF"):
            icc = src.info.get("icc_profile")
            if icc:
                save_kwargs["icc_profile"] = icc

        img.save(output_path, format=pillow_format, **save_kwargs)

    return output_path
