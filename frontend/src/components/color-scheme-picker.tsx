import { useTheme } from "@/components/theme-provider";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";

const colorSchemes = [
  {
    value: "neutral",
    label: "Neutral",
    description: "Classic gray for balanced design",
  },
  {
    value: "stone",
    label: "Stone",
    description: "Warm earth tones with subtle beige",
  },
  {
    value: "zinc",
    label: "Zinc",
    description: "Cool metallic gray with blue hints",
  },
  {
    value: "gray",
    label: "Gray",
    description: "Pure neutral gray, no color bias",
  },
  {
    value: "slate",
    label: "Slate",
    description: "Sophisticated blue-gray palette",
  },
] as const;

export const ColorSchemePicker = () => {
  const { colorScheme, setColorScheme } = useTheme();

  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="space-y-2">
        <Label className="text-sm font-medium">Color Palette</Label>
        <p className="text-sm text-muted-foreground">
          Choose the base color scheme for the interface
        </p>
      </div>

      <RadioGroup
        value={colorScheme}
        onValueChange={setColorScheme}
        className="flex flex-col flex-1 gap-2"
      >
        {colorSchemes.map((scheme) => (
          <label
            key={scheme.value}
            htmlFor={scheme.value}
            className="flex items-center gap-3 rounded-lg border p-4 cursor-pointer transition-colors hover:bg-accent/50 has-data-[state=checked]:bg-primary/5 has-data-[state=checked]:border-primary dark:has-data-[state=checked]:bg-primary/10 flex-1"
          >
            <div className="flex-1 space-y-1">
              <div className="text-sm font-medium leading-none">
                {scheme.label}
              </div>
              <p className="text-sm text-muted-foreground">
                {scheme.description}
              </p>
            </div>
            <RadioGroupItem value={scheme.value} id={scheme.value} />
          </label>
        ))}
      </RadioGroup>
    </div>
  );
};
