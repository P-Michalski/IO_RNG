import { Outlet } from "react-router-dom";
import { NavigationSidebar } from "./components/NavigationSidebar/navigation-sidebar";
import {
  SidebarProvider,
  SidebarInset,
  SidebarTrigger,
} from "./components/ui/sidebar";
import { ThemeProvider } from "./components/theme-provider";
import { Toaster } from "sonner";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "./components/ui/tooltip";
import { LanguageProvider } from "./contexts/language-context";
import { Footer } from "./components/Footer/footer";
import { TestResultsProvider } from "./contexts/test-results-context";

function App() {
  return (
    <ThemeProvider
      defaultTheme="dark"
      storageKey="vite-ui-theme"
      defaultColorScheme="neutral"
      colorSchemeStorageKey="vite-ui-color-scheme"
    >
      <LanguageProvider>
        <TestResultsProvider>
          <SidebarProvider>
            <div className="flex min-h-screen w-full">
              <NavigationSidebar />
              <SidebarInset className="flex flex-col flex-1 min-w-0">
                <header className="sticky top-0 z-10 bg-background border-b">
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <SidebarTrigger />
                    </TooltipTrigger>
                    <TooltipContent>Toggle Sidebar</TooltipContent>
                  </Tooltip>
                </header>
                <main className="flex-1">
                  <Outlet />
                </main>
                <Footer />
              </SidebarInset>
            </div>
            <Toaster />
          </SidebarProvider>
        </TestResultsProvider>
      </LanguageProvider>
    </ThemeProvider>
  );
}

export default App;
