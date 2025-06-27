// // api/dashboard.js
// export const getDashboardStats = async () => {
//     const res = await fetch("http://localhost:5050/api/summary");
//     const data = await res.json();
//     return {
//       totalSessions: data.total_sessions,
//       matchRate: data.match_success_rate,
//       recentSessions: data.last_24h_sessions,
//       newUsers: data.new_users,
//       trafficChange: data.traffic_change,
//       matchRateChange: data.match_rate_change,
//       recentChange: data.recent_change,
//       userChange: data.user_change,
//       weeklyStats: data.weekly_session_counts
//     };
//   };
  

// api/dashboard.js
export const getDashboardStats = async () => {
    const res = await fetch("http://localhost:5050/api/summary");
    const data = await res.json();
    return {
      totalSessions: data.total_sessions,
      matchRate: data.match_success_rate,
      recentSessions: data.last_24h_sessions,
      newUsers: data.new_users,
      trafficChange: data.traffic_change,
      matchRateChange: data.match_rate_change,
      recentChange: data.recent_change,
      userChange: data.user_change,
      weeklyStats: data.weekly_session_counts,
      matchRateStats: data.match_rate_trend,
      ageDistribution: data.age_distribution,
      regionDistribution: data.region_distribution,
      fieldDistribution: data.field_distribution
    };
  };
  