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
      className="h-14 px-6 text-lg bg-transparent border-border/20 focus:border-border/40 transition-colors placeholder:text-muted-foreground/40 placeholder:font-light"
      autoFocus
      {...props}
    />
  );
}
