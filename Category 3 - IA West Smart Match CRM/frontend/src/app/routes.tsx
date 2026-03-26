import { createBrowserRouter } from "react-router";
import { Layout } from "./components/Layout";
import { LandingPage } from "./pages/LandingPage";
import { LoginPage } from "./pages/LoginPage";
import { Dashboard } from "./pages/Dashboard";
import { Opportunities } from "./pages/Opportunities";
import { Volunteers } from "./pages/Volunteers";
import { AIMatching } from "./pages/AIMatching";
import { Pipeline } from "./pages/Pipeline";
import { Calendar } from "./pages/Calendar";
import { Outreach } from "./pages/Outreach";

export const router = createBrowserRouter([
  // Public routes (no sidebar)
  { path: "/", Component: LandingPage },
  { path: "/login", Component: LoginPage },

  // Coordinator routes (with sidebar layout — pathless layout route)
  {
    Component: Layout,
    children: [
      { path: "dashboard", Component: Dashboard },
      { path: "opportunities", Component: Opportunities },
      { path: "volunteers", Component: Volunteers },
      { path: "ai-matching", Component: AIMatching },
      { path: "pipeline", Component: Pipeline },
      { path: "calendar", Component: Calendar },
      { path: "outreach", Component: Outreach },
    ],
  },
]);
