// App.js
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";
import Jobs from "./pages/Jobs";
import JobDetail from "./pages/JobDetail";
import Sidebar from "./components/Sidebar";

function App() {
  return (
    <Router>
      <div className="flex min-h-screen">
        {/* 사이드바 고정 */}
        <Sidebar />
        
        {/* 본문 영역 */}
        <div className="ml-64 w-full">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/history" element={<History />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/jobs/:filename" element={<JobDetail />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
