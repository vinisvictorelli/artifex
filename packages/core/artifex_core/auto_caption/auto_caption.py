import os

import whisper


def mp3_to_srt(
    mp3_file: str,
    output_srt: str,
    max_chars_per_segment: int = 42,
    model_size: str = "medium",
) -> str:
    """
    Converte um arquivo de áudio em um arquivo de legendas SRT com segmentos
    ajustados por quantidade máxima de caracteres.

    Args:
        mp3_file: Caminho do arquivo de áudio de entrada.
        output_srt: Caminho onde o arquivo SRT gerado será salvo.
        max_chars_per_segment: Número máximo de caracteres por segmento.
        model_size: Modelo Whisper a usar ("tiny", "base", "small", "medium", "large").

    Returns:
        Caminho do arquivo SRT gerado.
    """
    model = whisper.load_model(model_size)

    result = model.transcribe(mp3_file, language="pt")

    os.makedirs(os.path.dirname(output_srt) or ".", exist_ok=True)
    with open(output_srt, "w", encoding="utf-8") as srt_file:
        index = 1
        for segment in result["segments"]:
            start = segment["start"]
            end = segment["end"]
            text = segment["text"]

            split_text = split_text_by_chars(text, max_chars_per_segment)
            segment_duration = (end - start) / len(split_text)

            for i, part in enumerate(split_text):
                part_start = start + i * segment_duration
                part_end = part_start + segment_duration

                srt_file.write(f"{index}\n")
                srt_file.write(f"{format_timestamp(part_start)} --> {format_timestamp(part_end)}\n")
                srt_file.write(f"{part}\n\n")
                index += 1

    return output_srt


def split_text_by_chars(text: str, max_chars: int) -> list[str]:
    """Divide um texto em partes com no máximo `max_chars` caracteres, sem cortar palavras."""
    words = text.split()
    lines = []
    current_line: list[str] = []

    for word in words:
        if len(" ".join(current_line + [word])) <= max_chars:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def format_timestamp(seconds: float) -> str:
    """Converte tempo em segundos para o formato SRT (hh:mm:ss,ms)."""
    millis = int(seconds * 1000)
    hours = millis // 3600000
    millis %= 3600000
    minutes = millis // 60000
    millis %= 60000
    secs = millis // 1000
    millis %= 1000
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"
