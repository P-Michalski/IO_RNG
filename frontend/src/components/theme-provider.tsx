import { createContext, useContext, useEffect, useState } from "react";

type Theme = "dark" | "light" | "system";
type ColorScheme = "neutral" | "stone" | "slate" | "gray" | "zinc";
type Accent =
  | "default"
  | "blue"
  | "green"
  | "orange"
  | "red"
  | "rose"
  | "violet"
  | "yellow";

type ThemeProviderProps = {
  children: React.ReactNode;
  defaultTheme?: Theme;
  defaultColorScheme?: ColorScheme;
  defaultAccent?: Accent;
  storageKey?: string;
  colorSchemeStorageKey?: string;
  accentStorageKey?: string;
};

type ThemeProviderState = {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  colorScheme: ColorScheme;
  setColorScheme: (colorScheme: ColorScheme) => void;
  accent: Accent;
  setAccent: (accent: Accent) => void;
};

const initialState: ThemeProviderState = {
  theme: "system",
  setTheme: () => null,
  colorScheme: "neutral",
  setColorScheme: () => null,
  accent: "default",
  setAccent: () => null,
};

const ThemeProviderContext = createContext<ThemeProviderState>(initialState);

export function ThemeProvider({
  children,
  defaultTheme = "system",
  defaultColorScheme = "neutral",
  defaultAccent = "default",
  storageKey = "vite-ui-theme",
  colorSchemeStorageKey = "vite-ui-color-scheme",
  accentStorageKey = "vite-ui-accent",
  ...props
}: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(
    () => (localStorage.getItem(storageKey) as Theme) || defaultTheme
  );

  const [colorScheme, setColorScheme] = useState<ColorScheme>(
    () =>
      (localStorage.getItem(colorSchemeStorageKey) as ColorScheme) ||
      defaultColorScheme
  );

  const [accent, setAccent] = useState<Accent>(
    () => (localStorage.getItem(accentStorageKey) as Accent) || defaultAccent
  );

  useEffect(() => {
    const root = window.document.documentElement;

    root.classList.remove("light", "dark");

    if (theme === "system") {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)")
        .matches
        ? "dark"
        : "light";

      root.classList.add(systemTheme);
      return;
    }

    root.classList.add(theme);
  }, [theme]);

  useEffect(() => {
    const root = window.document.documentElement;

    root.setAttribute("data-theme", colorScheme);
  }, [colorScheme]);

  useEffect(() => {
    const root = window.document.documentElement;

    root.setAttribute("data-accent", accent);
  }, [accent]);

  const value = {
    theme,
    setTheme: (theme: Theme) => {
      localStorage.setItem(storageKey, theme);
      setTheme(theme);
    },
    colorScheme,
    setColorScheme: (colorScheme: ColorScheme) => {
      localStorage.setItem(colorSchemeStorageKey, colorScheme);
      setColorScheme(colorScheme);
    },
    accent,
    setAccent: (accent: Accent) => {
      localStorage.setItem(accentStorageKey, accent);
      setAccent(accent);
    },
  };

  return (
    <ThemeProviderContext.Provider {...props} value={value}>
      {children}
    </ThemeProviderContext.Provider>
  );
}

export const useTheme = () => {
  const context = useContext(ThemeProviderContext);

  if (context === undefined)
    throw new Error("useTheme must be used within a ThemeProvider");

  return context;
};
