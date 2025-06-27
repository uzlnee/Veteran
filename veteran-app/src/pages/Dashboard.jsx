// const Home = () => {
//     return (
//       <div className="space-y-6">
//         <h2 className="text-2xl font-bold flex items-center gap-2">
//           🏠 베테랑 관리자 대시보드
//         </h2>
  
//         <section>
//           <h3 className="text-xl font-semibold flex items-center gap-2">
//             📊 주요 지표
//           </h3>
//           <div className="grid grid-cols-3 gap-4 mt-4">
//             <div className="p-4 rounded-lg shadow bg-white text-center">
//               <div className="text-sm text-gray-500">누적 상담 수</div>
//               <div className="text-xl font-bold">5건</div>
//             </div>
//             <div className="p-4 rounded-lg shadow bg-white text-center">
//               <div className="text-sm text-gray-500">매칭 성공률</div>
//               <div className="text-xl font-bold">68.5%</div>
//             </div>
//             <div className="p-4 rounded-lg shadow bg-white text-center">
//               <div className="text-sm text-gray-500">최근 상담(24h)</div>
//               <div className="text-xl font-bold">0건</div>
//             </div>
//           </div>
//         </section>
  
//         <section>
//           <h3 className="text-xl font-semibold flex items-center gap-2">
//             📈 주차별 상담 수 추이
//           </h3>
//           <p className="text-gray-500 text-sm mb-2">요일/날짜 기준</p>
//           {/* 여기에 그래프 또는 chart.js 등 컴포넌트 삽입 */}
//           <div className="mt-4 h-64 bg-gray-100 rounded-lg flex items-center justify-center">
//             그래프 영역
//           </div>
//         </section>
//       </div>
//     );
//   };
  
//   export default Home;

// import React from "react";

// export default function Dashboard() {
//   return (
//     <div>
//       <h1 className="text-2xl font-semibold mb-4">Dashboard</h1>
//       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
//         <div className="bg-white p-4 rounded shadow">Traffic</div>
//         <div className="bg-white p-4 rounded shadow">New Users</div>
//         <div className="bg-white p-4 rounded shadow">Sales</div>
//         <div className="bg-white p-4 rounded shadow">Performance</div>
//       </div>
//       <div className="bg-white mt-6 p-4 rounded shadow">Chart 영역</div>
//     </div>
//   );
// }
  

// import React from "react";

// const Dashboard = () => {
//   // 임시 mock 데이터
//   const weekData = [
//     { day: "월", date: "05/05", count: 0 },
//     { day: "화", date: "05/06", count: 0 },
//     { day: "수", date: "05/07", count: 1 },
//     { day: "목", date: "05/08", count: 0 },
//     { day: "금", date: "05/09", count: 0 },
//     { day: "토", date: "05/10", count: 0 },
//     { day: "일", date: "05/11", count: 0 },
//   ];

//   return (
//     <div className="min-h-screen bg-gray-50 font-pre px-6 py-6">
//       {/* 지표 카드 영역 */}
//       <div className="grid grid-cols-3 gap-6 mb-10">
//         <div className="bg-white rounded-lg shadow p-6">
//           <p className="text-sm text-gray-500">누적 상담 수</p>
//           <p className="text-2xl font-bold mt-2">5건</p>
//         </div>
//         <div className="bg-white rounded-lg shadow p-6">
//           <p className="text-sm text-gray-500">매칭 성공률</p>
//           <p className="text-2xl font-bold mt-2">68.5%</p>
//         </div>
//         <div className="bg-white rounded-lg shadow p-6">
//           <p className="text-sm text-gray-500">최근 상담 (24h)</p>
//           <p className="text-2xl font-bold mt-2">0건</p>
//         </div>
//       </div>

//       {/* 차트 + 선택 영역 */}
//       <div className="bg-white rounded-lg shadow p-6 mb-10">
//         <h2 className="text-lg font-semibold mb-6">📈 주차별 상담 수 추이 (요일/날짜 기준)</h2>

//         {/* 조회 주차 선택 */}
//         <div className="mb-4">
//           <label className="block text-sm font-medium text-gray-700 mb-1">조회할 주차 선택</label>
//           <select className="w-full border rounded px-3 py-2 text-sm">
//             <option>2025년 5월 1주차 (05/05~05/11)</option>
//             {/* 향후 옵션 추가 가능 */}
//           </select>
//         </div>

//         {/* 그래프 타입 선택 */}
//         <div className="mb-6">
//           <label className="block text-sm font-medium text-gray-700 mb-2">그래프 유형 선택</label>
//           <div className="flex items-center gap-4">
//             <label className="flex items-center gap-2 text-sm">
//               <input type="radio" name="chart" disabled />
//               막대그래프 (준비 중)
//             </label>
//             <label className="flex items-center gap-2 text-sm">
//               <input type="radio" name="chart" checked readOnly />
//               선형그래프
//             </label>
//           </div>
//         </div>

//         {/* 간단한 선형 그래프 mock */}
//         <div className="h-40 w-full border-t border-l relative">
//           {/* 간단한 라인 */}
//           <svg className="absolute left-0 top-0 w-full h-full">
//             <polyline
//               fill="none"
//               stroke="#3b82f6"
//               strokeWidth="2"
//               points="0,120 50,80 100,120 150,120 200,120 250,120 300,120"
//             />
//           </svg>
//           {/* 축 label */}
//           <div className="absolute bottom-0 flex justify-between text-[10px] text-gray-600 w-full px-1">
//             {weekData.map((d) => (
//               <span key={d.date}>{d.day} ({d.date})</span>
//             ))}
//           </div>
//         </div>
//       </div>

//       {/* 요약 테이블 */}
//       <div className="bg-white rounded-lg shadow p-6 mb-6">
//         <details open>
//           <summary className="font-semibold cursor-pointer">📋 상담 수 요약 테이블 보기</summary>
//           <div className="mt-4 overflow-x-auto">
//             <table className="w-full text-sm text-left border">
//               <thead>
//                 <tr className="bg-gray-100 border-b text-gray-700">
//                   <th className="p-2 border-r">요일</th>
//                   <th className="p-2 border-r">날짜</th>
//                   <th className="p-2">상담 수</th>
//                 </tr>
//               </thead>
//               <tbody>
//                 {weekData.map((d, idx) => (
//                   <tr key={idx} className="border-b">
//                     <td className="p-2 border-r">{d.day}</td>
//                     <td className="p-2 border-r">{d.date}</td>
//                     <td className="p-2">{d.count}</td>
//                   </tr>
//                 ))}
//               </tbody>
//             </table>
//           </div>
//         </details>
//       </div>

//       {/* 다운로드 버튼 */}
//       <div className="text-right">
//         <button className="bg-blue-100 text-blue-700 px-4 py-2 rounded text-sm font-medium hover:bg-blue-200">
//           📥 상담 수 데이터 CSV 다운로드
//         </button>
//       </div>
//     </div>
//   );
// };

// export default Dashboard;

import React, { useEffect, useState } from "react";
import CardStat from "../components/CardStat";
import LineChart from "../components/LineChart";
import PieChart from "../components/PieChart";
import { getDashboardStats } from "../api/dashboard";
import {
  FaUserPlus,
  FaComments,
  FaHandshake,
  FaChartLine
} from "react-icons/fa";

const Dashboard = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      const result = await getDashboardStats();
      setStats(result);
    };
    fetchStats();
  }, []);

  if (!stats) return <div className="p-6">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-100 px-6 py-8 font-pre">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Dashboard</h1>

      {/* KPI 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <CardStat title="상담 총 횟수" value={stats.totalSessions} change={stats.trafficChange} icon={<FaComments />} />
        <CardStat title="신규 사용자 수" value={stats.newUsers} change={stats.userChange} icon={<FaUserPlus />} />
        <CardStat title="매칭 성공률" value={`${stats.matchRate}%`} change={stats.matchRateChange} icon={<FaHandshake />} />
        <CardStat title="최근 24시간 상담" value={stats.recentSessions} change={stats.recentChange} icon={<FaChartLine />} />
      </div>

      {/* 중간 섹션: 라인 차트 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <LineChart title="주간 상담 수 추이" data={stats.weeklyStats} dataKey="count" />
        <LineChart title="매칭 성공률 추이" data={stats.matchRateStats} dataKey="rate" />
      </div>

      {/* 하단 섹션: 파이 차트 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <PieChart title="연령대별 사용자 비중" data={stats.ageDistribution} />
        <PieChart title="지역별 상담 분포" data={stats.regionDistribution} />
        <PieChart title="희망 분야 분포" data={stats.fieldDistribution} />
      </div>
    </div>
  );
};

export default Dashboard;
