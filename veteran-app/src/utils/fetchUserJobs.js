// utils/fetchUserJobs.js
export const fetchUserJobs = async (name, date) => {
    const encodedName = encodeURIComponent(name);
    const url = `/user_jobs/${encodedName}_${date}.json`;
  
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error("❌ Failed to fetch job data:", err);
      return null;
    }
  };
  