import { HashRouter, Navigate, Route, Routes } from "react-router-dom";
import { Report } from "./pages/Report";
import { Settings } from "./pages/Settings";

function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/settings" replace />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/report" element={<Report />} />
      </Routes>
    </HashRouter>
  );
}

export default App;
