import { useTheme } from "@/components/theme-provider";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";

const accents = [
  {
    value: "default",
    label: "Default",
    color: "oklch(0.708 0 0)",
    description: "Classic gray without color tint",
  },
  {
    value: "blue",
    label: "Blue",
    color: "oklch(0.488 0.243 264.376)",
    description: "Classic blue accent",
  },
  {
    value: "green",
    label: "Green",
    color: "oklch(0.648 0.2 131.684)",
    description: "Fresh green accent",
  },
  {
    value: "orange",
    label: "Orange",
    color: "oklch(0.646 0.222 41.116)",
    description: "Warm orange accent",
  },
  {
    value: "red",
    label: "Red",
    color: "oklch(0.577 0.245 27.325)",
    description: "Dynamic red accent",
  },
  {
    value: "rose",
    label: "Rose",
    color: "oklch(0.586 0.253 17.585)",
    description: "Delicate rose accent",
  },
  {
    value: "violet",
    label: "Violet",
    color: "oklch(0.541 0.281 293.009)",
    description: "Creative violet accent",
  },
  {
    value: "yellow",
    label: "Yellow",
    color: "oklch(0.852 0.199 91.936)",
    description: "Energetic yellow accent",
  },
] as const;

export const AccentSelector = () => {
  const { accent, setAccent } = useTheme();

  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="space-y-2">
        <Label className="text-sm font-medium">Accent Color</Label>
        <p className="text-sm text-muted-foreground">
          Choose the color for buttons and interactive elements
        </p>
      </div>

      <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-3">
        <RadioGroup
          value={accent}
          onValueChange={setAccent}
          className="contents"
        >
          {accents.map((item) => (
            <label
              key={item.value}
              htmlFor={item.value}
              className="flex items-center gap-3 rounded-lg border p-4 cursor-pointer transition-colors hover:bg-accent/50 has-data-[state=checked]:bg-primary/5 has-data-[state=checked]:border-primary dark:has-data-[state=checked]:bg-primary/10"
            >
              <div
                className="h-6 w-6 rounded-full border-2 border-border shrink-0"
                style={{ backgroundColor: item.color }}
              />
              <div className="flex-1 min-w-0 space-y-0.5">
                <div className="text-sm font-medium leading-none">
                  {item.label}
                </div>
                <p className="text-xs text-muted-foreground">
                  {item.description}
                </p>
              </div>
              <RadioGroupItem value={item.value} id={item.value} />
            </label>
          ))}
        </RadioGroup>
      </div>
    </div>
  );
};
