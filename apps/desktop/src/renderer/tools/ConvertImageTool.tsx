import { useState } from "react";
import { ToolCard } from "../components/ToolCard";
import { PathInput } from "../components/PathInput";
import { FormatSelect } from "../components/FormatSelect";
import { api } from "../lib/api";
import {
  IMAGE_FILTERS,
  IMAGE_FORMATS,
  IMAGE_QUALITY_FORMATS,
  filtersForFormat,
  swapExtension,
} from "../lib/pathFilters";

export function ConvertImageTool() {
  const [imagePath, setImagePath] = useState("");
  const [outputPath, setOutputPath] = useState("");
  const [format, setFormat] = useState(IMAGE_FORMATS[0].value);
  const [quality, setQuality] = useState(90);

  function handleFormatChange(next: string) {
    setFormat(next);
    setOutputPath((prev) => (prev ? swapExtension(prev, next) : prev));
  }

  return (
    <ToolCard
      title="Converter imagem"
      description="Converte uma imagem para outro formato."
      runLabel="Converter"
      onRun={() =>
        api.convertImage({
          image_path: imagePath,
          output_path: outputPath || undefined,
          format,
          quality: IMAGE_QUALITY_FORMATS.includes(format) ? quality : undefined,
        })
      }
    >
      <PathInput
        label="Imagem de entrada"
        value={imagePath}
        onChange={setImagePath}
        placeholder="./imagem.png"
        mode="file"
        filters={IMAGE_FILTERS}
      />
      <FormatSelect
        label="Formato de saída"
        value={format}
        options={IMAGE_FORMATS}
        onChange={handleFormatChange}
      />
      {IMAGE_QUALITY_FORMATS.includes(format) && (
        <label className="flex flex-col gap-1">
          <span className="text-[11px] text-neutral-500">Qualidade ({quality})</span>
          <input
            type="range"
            min={1}
            max={100}
            value={quality}
            onChange={(e) => setQuality(Number(e.target.value))}
            className="accent-accent"
          />
        </label>
      )}
      <PathInput
        label="Imagem de saída (opcional)"
        value={outputPath}
        onChange={setOutputPath}
        placeholder="./imagem.jpg"
        mode="save"
        filters={filtersForFormat(format)}
      />
    </ToolCard>
  );
}
