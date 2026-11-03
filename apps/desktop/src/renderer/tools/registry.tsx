import type { ComponentType } from "react";
import { AudioLines, Captions, Download, Image, Scissors, type LucideIcon } from "lucide-react";
import { DownloadTool } from "./DownloadTool";
import { ExtractAudioTool } from "./ExtractAudioTool";
import { AutoCaptionTool } from "./AutoCaptionTool";
import { AutoCutTool } from "./AutoCutTool";
import { ConvertImageTool } from "./ConvertImageTool";

export type ToolDef = {
  id: string;
  label: string;
  description: string;
  icon: LucideIcon;
  Component: ComponentType;
};

// A ordem aqui é a ordem do menu; o primeiro item é a aba padrão.
export const tools: ToolDef[] = [
  {
    id: "download",
    label: "Baixar vídeo",
    description: "Baixa um vídeo a partir de uma URL.",
    icon: Download,
    Component: DownloadTool,
  },
  {
    id: "extract-audio",
    label: "Extrair áudio",
    description: "Extrai a trilha de áudio de um vídeo.",
    icon: AudioLines,
    Component: ExtractAudioTool,
  },
  {
    id: "auto-caption",
    label: "Legendas automáticas",
    description: "Gera legendas .srt com Whisper.",
    icon: Captions,
    Component: AutoCaptionTool,
  },
  {
    id: "auto-cut",
    label: "Corte automático",
    description: "Remove silêncios do vídeo.",
    icon: Scissors,
    Component: AutoCutTool,
  },
  {
    id: "convert-image",
    label: "Converter imagem",
    description: "Converte imagens entre PNG, JPEG, GIF e outros.",
    icon: Image,
    Component: ConvertImageTool,
  },
];
