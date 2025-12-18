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

function App() {
  return (
    <ThemeProvider
      defaultTheme="dark"
      storageKey="vite-ui-theme"
      defaultColorScheme="neutral"
      colorSchemeStorageKey="vite-ui-color-scheme"
    >
      <SidebarProvider>
        <NavigationSidebar />
        <main>
          <Tooltip>
            <TooltipTrigger asChild>
              <SidebarTrigger className="sticky top-0" />
            </TooltipTrigger>
            <TooltipContent>Toggle Sidebar</TooltipContent>
          </Tooltip>
        </main>
        <Outlet />
        <Toaster />
      </SidebarProvider>
    </ThemeProvider>
  );
}

export default App;
