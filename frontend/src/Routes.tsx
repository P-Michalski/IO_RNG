import App from "./App";
import {
  createBrowserRouter,
  Navigate,
  type RouteObject,
} from "react-router-dom";
import { Dashboard } from "./components/Dashboard/dashboard";
import { Tests } from "./components/Tests/tests";
import { Results } from "./components/Results/results";
import { Generator } from "./components/Generator/generator";
import { Wiki } from "./components/Wiki/wiki";
import { AlgorithmsWiki } from "./components/Wiki/AlgorithmsWiki/algorithms-wiki";
import { MethodologyWiki } from "./components/Wiki/MethodologyWiki/methodology-wiki";
import { Settings } from "./components/Settings/settings";
import { NotFound } from "./components/NotFound/not-found";
import { About } from "./components/About/about";

export const routes: RouteObject[] = [
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "/generator", element: <Generator /> },
      { path: "/tests", element: <Tests /> },
      { path: "/results", element: <Results /> },

      { path: "/wiki", element: <Navigate to="/wiki/algorithms" replace /> },
      { path: "/wiki/algorithms", element: <AlgorithmsWiki /> },
      { path: "/wiki/methodology", element: <MethodologyWiki /> },

      { path: "/about", element: <About /> },
      { path: "/settings", element: <Settings /> },

      { path: "not-found", element: <NotFound /> },
      { path: "*", element: <Navigate to="/not-found" replace /> },
    ],
  },
];

export const router = createBrowserRouter(routes);
