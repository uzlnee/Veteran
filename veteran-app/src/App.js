// import { useState } from 'react';
// import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// import Sidebar from './components/Sidebar';
// import Home from './pages/Home';
// import Log from './pages/Log';
// import Recommendation from './pages/Recommendation';

// function App() {
//   const [sidebarOpen, setSidebarOpen] = useState(false);

//   return (
//     <Router>
//       <div className="flex h-screen overflow-hidden">
//         <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />
//         <div className="flex-1 flex flex-col">
//           <header className="p-4 shadow-sm flex justify-between items-center">
//             <h1 className="text-xl font-bold">📊 관리자</h1>
//             <button
//               className="md:hidden p-2"
//               onClick={() => setSidebarOpen(!sidebarOpen)}
//             >
//               ☰
//             </button>
//           </header>
//           <main className="p-6 overflow-y-auto">
//             <Routes>
//               <Route path="/" element={<Home />} />
//               <Route path="/log" element={<Log />} />
//               <Route path="/recommendation" element={<Recommendation />} />
//             </Routes>
//           </main>
//         </div>
//       </div>
//     </Router>
//   );
// }

// export default App;

// // src/App.js
// import React from "react";
// import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
// import AdminLayout from "./layouts/AdminLayout";

// export default function App() {
//   return (
//     <BrowserRouter>
//       <Routes>
//         <Route path="/admin/*" element={<AdminLayout />} />
//         <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
//       </Routes>
//     </BrowserRouter>
//   );
// }

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";
import Jobs from "./pages/Jobs";
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
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/history" element={<History />} />
            <Route path="/jobs" element={<Jobs />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
