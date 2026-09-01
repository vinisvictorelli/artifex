type PathInputProps = {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
};

export function PathInput({ label, value, onChange, placeholder }: PathInputProps) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-[11px] text-neutral-500">{label}</span>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="rounded-md bg-surface border border-white/10 px-2.5 py-1.5 text-xs text-neutral-200 focus:outline-none focus:border-accent"
      />
    </label>
  );
}
