import type { FormatOption } from "../lib/pathFilters";

type FormatSelectProps = {
  label: string;
  value: string;
  options: FormatOption[];
  onChange: (value: string) => void;
};

export function FormatSelect({ label, value, options, onChange }: FormatSelectProps) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-[11px] text-neutral-500">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-md bg-surface border border-white/10 px-2.5 py-1.5 text-xs text-neutral-200 focus:outline-none focus:border-accent"
      >
        {options.map((o) => (
          <option key={o.value} value={o.value} className="bg-panel text-neutral-200">
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}
