const BASE_URL = "/api";

export async function getUserJobs(name, date) {
  try {
    const filename = encodeURIComponent(`${name}_${date}.json`);
    const response = await fetch(`${BASE_URL}/jobs/${filename}`);
    if (!response.ok) throw new Error("Network response was not ok");
    return await response.json();
  } catch (error) {
    console.error("Error fetching job data:", error);
    return null;
  }
}

export const getDashboardStats = async () => {
    const res = await fetch("/api/summary"); // 절대경로 X, 상대경로 O
    // ...
};

export async function getJobFiles() {
  try {
    const response = await fetch(`${BASE_URL}/jobs/files`);
    if (!response.ok) throw new Error("Network response was not ok");
    return await response.json();
  } catch (error) {
    console.error("Error fetching job files:", error);
    return [];
  }
}
