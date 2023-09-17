import { ModeToggle } from "@/components/ui/mode-toggle";
import React from "react";

const Header: React.FC = () => {
  return (
    <nav className="max-w-screen-lg py-2 m-auto">
      <div
        className="flex justify-between items-center h-16 relative"
        role="navigation"
      >
        <span className="flex flex-row items-center jusify-center gap-2 text-xl font-semibold">
          <img src="ear.png" alt="logo" className="h-10 w-10 ml-4" />
          Placeholder
        </span>
        <ModeToggle />
      </div>
    </nav>
  );
};

export default Header;
