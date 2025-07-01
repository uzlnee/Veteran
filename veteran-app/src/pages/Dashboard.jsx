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
    <div className="min-h-screen bg-gray-100 font-pre">
      {/* 상단 파란 헤더 (사진처럼) */}
      <div className="bg-blue-500 px-6 py-4">
        <h2 className="text-xl font-semibold text-white tracking-widest">DASHBOARD</h2>
      </div>
      {/* 아래 컨텐츠는 기존 마진 유지 */}
      <div className="px-6 py-8">
        {/* KPI 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <CardStat title="상담 총 횟수" value={stats.totalSessions} change={stats.trafficChange} icon={<FaComments />} />
          <CardStat title="신규 사용자 수" value={stats.newUsers} change={stats.userChange} icon={<FaUserPlus />} />
          <CardStat title="매칭 성공률" value={`${stats.matchRate}%`} change={stats.matchRateChange} icon={<FaHandshake />} />
          <CardStat title="최근 24시간 상담" value={stats.recentSessions} change={stats.recentChange} icon={<FaChartLine />} />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <LineChart title="주간 상담 수 추이" data={stats.weeklyStats} dataKey="count" />
          <LineChart title="매칭 성공률 추이" data={stats.matchRateStats} dataKey="rate" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <PieChart title="연령대별 사용자 비중" data={stats.ageDistribution} />
          <PieChart title="지역별 상담 분포" data={stats.regionDistribution} />
          <PieChart title="희망 분야 분포" data={stats.fieldDistribution} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
