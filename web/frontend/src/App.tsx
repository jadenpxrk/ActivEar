import "./App.css";

import Header from "@/components/sections/header";
import Landing from "@/components/sections/landing";
import React from "react";
import { ThemeProvider } from "@/components/ui/theme-provider";

const AiAssistant: React.FC = () => {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <Header />
      <Landing />
    </ThemeProvider>
  );
};

export default AiAssistant;
