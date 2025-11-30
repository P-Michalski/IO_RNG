import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarGroupLabel,
  SidebarMenuSub,
  SidebarMenuSubItem,
  useSidebar,
} from "../ui/sidebar";
import {
  LayoutDashboard,
  Cpu as GeneratorIcon,
  TestTubeDiagonal as TestsIcon,
  FileChartColumn as ResultsIcon,
  BookOpen as WikiIcon,
  Settings as SettingsIcon,
  BookCheck as MethodologyIcon,
  Puzzle as AlgorithmsIcon,
  Info as AboutIcon,
  ChevronRight,
} from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "../ui/collapsible";
import { NavLink } from "react-router";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import { ModeToggle } from "../mode-toggle";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import githubWhite from "../../../src/assets/github/github-mark-white.png";
import githubDark from "../../../src/assets/github/github-mark.png";
import { useTheme } from "../theme-provider";

interface MenuItem {
  label: string;
  path: string;
  icon: React.ReactNode;
}

export const NavigationSidebar = () => {
  const { state } = useSidebar();
  const isCollapsed = state === "collapsed";

  const { theme } = useTheme();

  const ghRepo = {
    name: "IO_RNG",
    url: "https://github.com/P-Michalski/IO_RNG",
    icon: (
      <AvatarImage
        src={theme === "light" ? githubDark : githubWhite}
        alt="GitHub Repository"
      />
    ),
    description: "GitHub Repo",
  };

  const menuItems: MenuItem[] = [
    {
      label: "Dashboard",
      path: "/",
      icon: <LayoutDashboard className="size-6!" />,
    },
    {
      label: "Generator",
      path: "/generator",
      icon: <GeneratorIcon className="size-6!" />,
    },
    {
      label: "Tests",
      path: "/tests",
      icon: <TestsIcon className="size-6!" />,
    },
    {
      label: "Results",
      path: "/results",
      icon: <ResultsIcon className="size-6!" />,
    },
  ];

  const infoItems: MenuItem[] = [
    {
      label: "About",
      path: "/about",
      icon: <AboutIcon className="size-6!" />,
    },
    {
      label: "Wiki",
      path: "/wiki",
      icon: <WikiIcon className="size-6!" />,
    },
  ];

  const wikiItems: MenuItem[] = [
    {
      label: "Algorithms",
      path: "/wiki/algorithms",
      icon: <AlgorithmsIcon className="text-foreground" />,
    },
    {
      label: "Methodology",
      path: "/wiki/methodology",
      icon: <MethodologyIcon className="text-foreground" />,
    },
  ];

  const settingsItem: MenuItem = {
    label: "Settings",
    path: "/settings",
    icon: <SettingsIcon className="size-6!" />,
  };

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader></SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Overview</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {/* Basic navigation items */}
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.label}>
                  <SidebarMenuButton
                    asChild
                    className="pl-1! group-data-[collapsible=icon]:p-1!"
                    tooltip={item.label}
                  >
                    <NavLink to={item.path}>
                      {item.icon}
                      <span>{item.label}</span>
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Info</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {infoItems.map((item) =>
                item.label === "Wiki" ? (
                  isCollapsed ? (
                    // Dropdown dla zwiniętego sidebara
                    <SidebarMenuItem key={item.label}>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <SidebarMenuButton
                            className="pl-1! group-data-[collapsible=icon]:p-1!"
                            tooltip={item.label}
                          >
                            {item.icon}
                            <span>{item.label}</span>
                          </SidebarMenuButton>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent side="right" align="start">
                          {wikiItems.map((subItem) => (
                            <DropdownMenuItem key={subItem.label} asChild>
                              <NavLink
                                to={subItem.path}
                                className="flex items-center gap-2 cursor-pointer"
                              >
                                {subItem.icon}
                                <span>{subItem.label}</span>
                              </NavLink>
                            </DropdownMenuItem>
                          ))}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </SidebarMenuItem>
                  ) : (
                    // Collapsible dla rozwiniętego sidebara
                    <Collapsible
                      key={item.label}
                      defaultOpen
                      className="group/collapsible"
                    >
                      <SidebarMenuItem>
                        <CollapsibleTrigger asChild>
                          <SidebarMenuButton className="justify-between pl-1! group-data-[collapsible=icon]:p-1!">
                            <div className="flex items-center gap-2">
                              {item.icon}
                              <span>{item.label}</span>
                            </div>
                            <ChevronRight className="h-4 w-4 shrink-0 opacity-50 transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
                          </SidebarMenuButton>
                        </CollapsibleTrigger>
                        <CollapsibleContent>
                          <SidebarMenuSub>
                            {wikiItems.map((subItem) => (
                              <SidebarMenuSubItem key={subItem.label}>
                                <SidebarMenuButton asChild>
                                  <NavLink to={subItem.path}>
                                    {subItem.icon}
                                    <span>{subItem.label}</span>
                                  </NavLink>
                                </SidebarMenuButton>
                              </SidebarMenuSubItem>
                            ))}
                          </SidebarMenuSub>
                        </CollapsibleContent>
                      </SidebarMenuItem>
                    </Collapsible>
                  )
                ) : (
                  <SidebarMenuItem key={item.label}>
                    <SidebarMenuButton
                      asChild
                      className="pl-1! group-data-[collapsible=icon]:p-1!"
                      tooltip={item.label}
                    >
                      <NavLink to={item.path}>
                        {item.icon}
                        <span>{item.label}</span>
                      </NavLink>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                )
              )}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>App Settings</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton
                  asChild
                  className="pl-1! group-data-[collapsible=icon]:p-1!"
                  tooltip={settingsItem.label}
                >
                  <NavLink to={settingsItem.path}>
                    {settingsItem.icon}
                    <span>{settingsItem.label}</span>
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="p-2">
        <div className="flex group-data-[collapsible=icon]:flex-col items-center gap-2 transition-[flex-direction] duration-300 ease-in-out">
          <SidebarMenuButton
            size="lg"
            className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground flex-1 group-data-[collapsible=icon]:flex-none transition-[flex] duration-300 ease-in-out"
            asChild
            tooltip={ghRepo.description}
          >
            <a
              href={ghRepo.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2"
            >
              <Avatar className="h-8 w-8 rounded-lg">
                {ghRepo.icon}
                <AvatarFallback className="rounded-lg">GH</AvatarFallback>
              </Avatar>
              <div className="grid flex-1 text-left text-sm leading-tight overflow-hidden transition-[width,opacity] duration-300 ease-in-out group-data-[collapsible=icon]:w-0 group-data-[collapsible=icon]:opacity-0">
                <span className="truncate font-medium">{ghRepo.name}</span>
                <span className="truncate text-xs">{ghRepo.description}</span>
              </div>
            </a>
          </SidebarMenuButton>
          <div className="transition-transform duration-300 ease-in-out">
            <ModeToggle />
          </div>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
};
