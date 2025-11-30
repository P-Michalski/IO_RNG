import { Outlet } from "react-router-dom";
import { NavigationSidebar } from "./components/NavigationSidebar/navigation-sidebar";
import { SidebarProvider, SidebarTrigger } from "./components/ui/sidebar";

function App() {
  return (
    <SidebarProvider>
      <NavigationSidebar />
      <main>
        <SidebarTrigger />
        <Outlet />
      </main>
    </SidebarProvider>
  );
}

export default App;
