import { Languages } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useLanguage } from "@/contexts/language-context";
import GB from "country-flag-icons/react/3x2/GB";
import PL from "country-flag-icons/react/3x2/PL";
import { type ComponentType, type SVGProps } from "react";

interface LanguageConfig {
  code: string;
  name: string;
  FlagComponent: ComponentType<SVGProps<SVGElement>>;
}

const supportedLanguages: LanguageConfig[] = [
  { code: "en", name: "English", FlagComponent: GB },
  { code: "pl", name: "Polski", FlagComponent: PL },
];

export const LanguageSwitcher = () => {
  const { language, setLanguage } = useLanguage();

  const currentLanguage =
    supportedLanguages.find((lang) => lang.code === language) ||
    supportedLanguages[0];

  const CurrentFlag = currentLanguage.FlagComponent;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <CurrentFlag className="h-4 w-6" />
          {currentLanguage.name}
          <Languages className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {supportedLanguages.map((lang) => {
          const FlagComponent = lang.FlagComponent;
          return (
            <DropdownMenuItem
              key={lang.code}
              onClick={() => setLanguage(lang.code as any)}
              className="gap-2 cursor-pointer"
            >
              <FlagComponent className="h-4 w-6" />
              <span>{lang.name}</span>
              {lang.code === language && (
                <span className="ml-auto text-primary">✓</span>
              )}
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
