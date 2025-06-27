

export async function getUserJobs(name, date) {
  try {
    const filename = encodeURIComponent(`${name}_${date}.json`);
    const response = await fetch(`/api/jobs/${filename}`);
    if (!response.ok) throw new Error("Network response was not ok");
    return await response.json();
  } catch (error) {
    console.error("Error fetching job data:", error);
    return null;
  }
}
