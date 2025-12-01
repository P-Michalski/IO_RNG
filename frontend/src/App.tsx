import { Outlet } from "react-router-dom";
import { NavigationSidebar } from "./components/NavigationSidebar/navigation-sidebar";
import { SidebarProvider, SidebarTrigger } from "./components/ui/sidebar";
import { ThemeProvider } from "./components/theme-provider";

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <SidebarProvider>
        <NavigationSidebar />
        <SidebarTrigger />
        <Outlet />
      </SidebarProvider>
    </ThemeProvider>
  );
}

export default App;
