import { Outlet } from "react-router-dom";
import { NavigationSidebar } from "./components/NavigationSidebar/navigation-sidebar";
import { SidebarProvider, SidebarTrigger } from "./components/ui/sidebar";
import { ThemeProvider } from "./components/theme-provider";
import { Toaster } from "sonner";

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <SidebarProvider>
        <NavigationSidebar />
        <main>
          <SidebarTrigger className="sticky top-0" />
        </main>
        <Outlet />
        <Toaster />
      </SidebarProvider>
    </ThemeProvider>
  );
}

export default App;
