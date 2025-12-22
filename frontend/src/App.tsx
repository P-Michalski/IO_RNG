import { Outlet } from "react-router-dom";
import { NavigationSidebar } from "./components/NavigationSidebar/navigation-sidebar";
import { SidebarProvider, SidebarTrigger } from "./components/ui/sidebar";
import { ThemeProvider } from "./components/theme-provider";
import { Toaster } from "sonner";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "./components/ui/tooltip";
import { LanguageProvider } from "./contexts/language-context";
import { Footer } from "./components/Footer/footer";

function App() {
  return (
    <ThemeProvider
      defaultTheme="dark"
      storageKey="vite-ui-theme"
      defaultColorScheme="neutral"
      colorSchemeStorageKey="vite-ui-color-scheme"
    >
      <LanguageProvider>
        <SidebarProvider>
          <NavigationSidebar />
          <main className="flex flex-col min-h-screen w-full">
            <div className="flex-1">
              <Tooltip>
                <TooltipTrigger asChild>
                  <SidebarTrigger className="sticky top-0" />
                </TooltipTrigger>
                <TooltipContent>Toggle Sidebar</TooltipContent>
              </Tooltip>

              <Outlet />
            </div>
            <Footer />
          </main>
          <Toaster />
        </SidebarProvider>
      </LanguageProvider>
    </ThemeProvider>
  );
}

export default App;
