import { AccentSelector } from "../accent-selector";
import { ColorSchemePicker } from "../color-scheme-picker";
import { ThemeShowcase } from "./ThemeShowcase/theme-showcase";
import { Card, CardContent } from "../ui/card";
import { Separator } from "../ui/separator";

export const Settings = () => {
  return (
    <div className="container mx-auto max-w-7xl p-8 space-y-4">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Customize the appearance and behavior of the application
        </p>
      </div>

      <Separator />

      {/* Theme Configuration + Showcase */}
      <div className="grid gap-8 lg:grid-cols-[400px_1fr]">
        <Card className="flex flex-col">
          <CardContent className="flex-1 flex flex-col space-y-6">
            <ColorSchemePicker />
            <Separator />
            <AccentSelector />
          </CardContent>
        </Card>

        {/* Component Showcase - desktop */}
        <div className="hidden lg:flex lg:flex-col space-y-4">
          <div className="space-y-2">
            <h2 className="text-2xl font-semibold tracking-tight">
              Component Showcase
            </h2>
            <p className="text-muted-foreground">
              Preview how different UI components look with your selected theme
            </p>
          </div>
          <ThemeShowcase />
        </div>
      </div>

      {/* Component Showcase - mobile */}
      <div className="lg:hidden space-y-4">
        <Separator />
        <div className="space-y-2">
          <h2 className="text-2xl font-semibold tracking-tight">
            Component Showcase
          </h2>
          <p className="text-muted-foreground">
            Preview how different UI components look with your selected theme
          </p>
        </div>
        <ThemeShowcase />
      </div>
    </div>
  );
};
