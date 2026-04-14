import React from "react";
import { createRoot } from "react-dom/client";

import App from "./App";
import "./index.css";

const rootEl = document.getElementById("student-dashboard-root");
const dataEl = document.getElementById("student-dashboard-data");
const csrfEl = document.getElementById("student-csrf-token");

if (rootEl && dataEl) {
  let payload = null;
  try {
    payload = JSON.parse(dataEl.textContent || "{}");
    payload.csrfToken = (csrfEl && csrfEl.dataset && csrfEl.dataset.token) || "";
  } catch (error) {
    payload = null;
    console.error("Dashboard payload parse failed", error);
  }

  if (payload) {
    createRoot(rootEl).render(
      <React.StrictMode>
        <App payload={payload} />
      </React.StrictMode>
    );
  }
}
