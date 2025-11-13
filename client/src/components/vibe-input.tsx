import { Input } from "@/components/ui/input";

interface VibeInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  onKeyPress: (e: React.KeyboardEvent) => void;
  placeholder: string;
  disabled?: boolean;
}

export function VibeInput({
  value,
  onChange,
  onKeyPress,
  placeholder,
  disabled,
  ...props
}: VibeInputProps) {
  return (
    <Input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      onKeyPress={onKeyPress}
      placeholder={placeholder}
      disabled={disabled}
      className="h-14 px-6 text-lg bg-transparent border-2 border-purple-500/30 focus:border-purple-400/70 focus:ring-2 focus:ring-purple-500/20 transition-all duration-300 placeholder:text-muted-foreground/40 placeholder:font-light shadow-[0_0_15px_rgba(168,85,247,0.1)] focus:shadow-[0_0_25px_rgba(168,85,247,0.25)]"
      autoFocus
      {...props}
    />
  );
}
