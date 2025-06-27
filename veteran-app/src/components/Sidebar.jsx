// import { Link, useLocation } from 'react-router-dom';

// const Sidebar = ({ open, setOpen }) => {
//   const location = useLocation();
//   const links = [
//     { path: '/', label: '홈' },
//     { path: '/log', label: '상담 내역' },
//     { path: '/recommendation', label: '공고 추천' },
//   ];

//   return (
//     <div className={`fixed z-30 inset-y-0 left-0 w-64 bg-gray-100 transform ${open ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-200 ease-in-out md:translate-x-0 md:static md:inset-0`}>
//       <div className="p-4 font-bold text-lg">📈 베테랑 관리자</div>
//       <nav className="flex flex-col gap-2 p-4">
//         {links.map(link => (
//           <Link
//             key={link.path}
//             to={link.path}
//             className={`px-4 py-2 rounded-md hover:bg-blue-100 ${
//               location.pathname === link.path ? 'bg-blue-200 font-bold' : ''
//             }`}
//             onClick={() => setOpen(false)}
//           >
//             {link.label}
//           </Link>
//         ))}
//       </nav>
//     </div>
//   );
// };

// export default Sidebar;

import React from "react";
import { NavLink } from "react-router-dom";
import { FaDesktop, FaBriefcase, FaTable } from "react-icons/fa";

const Sidebar = () => {
  return (
    <div className="h-screen w-64 bg-white border-r text-sm px-6 py-8 font-pre">
      <h1 className="text-xl font-bold text-gray-800 mb-6 tracking-wide">VETERAN</h1>
      <hr className="mb-6 border-gray-200" />

      <p className="text-gray-500 text-xs font-bold mb-4 tracking-widest">ADMIN PAGES</p>

      <nav className="flex flex-col gap-4 text-gray-700">
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            `flex items-center gap-3 px-2 py-1.5 rounded-md font-bold ${
              isActive ? "text-blue-500" : "hover:text-blue-500"
            }`
          }
        >
          <FaDesktop className="text-base" />
          DASHBOARD
        </NavLink>

        <NavLink
          to="/history"
          className={({ isActive }) =>
            `flex items-center gap-3 px-2 py-1.5 rounded-md font-bold ${
              isActive ? "text-blue-500" : "hover:text-blue-500"
            }`
          }
        >
          <FaTable className="text-base" />
          HISTORY
        </NavLink>

        <NavLink
          to="/jobs"
          className={({ isActive }) =>
            `flex items-center gap-3 px-2 py-1.5 rounded-md font-bold ${
              isActive ? "text-blue-500" : "hover:text-blue-500"
            }`
          }
        >
          <FaBriefcase className="text-base" />
          JOBS
        </NavLink>
      </nav>
    </div>
  );
};

export default Sidebar;
