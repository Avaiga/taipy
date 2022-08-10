import React from "react";
import { createRoot } from "react-dom/client"
import { Router } from "taipy-gui";

const container = document.getElementById("root");
if (container) {
    const root = createRoot(container);
    root.render(<Router />);
}