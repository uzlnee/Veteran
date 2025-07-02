// src/api/history.js
const BASE_URL = "/api";

/**
 * 전체 세션 리스트 가져오기
 */
export async function fetchSessions() {
  const res = await fetch(`${BASE_URL}/sessions`);
  if (!res.ok) throw new Error("세션 목록 불러오기 실패");
  return res.json();
}

/**
 * 세션별 메타데이터 가져오기
 */
export async function fetchMetadata(sessionId) {
  const res = await fetch(`${BASE_URL}/sessions/${sessionId}/metadata`);
  if (!res.ok) throw new Error("메타데이터 불러오기 실패");
  return res.json();
}

/**
 * 세션별 transcript 가져오기
 */
export async function fetchTranscript(sessionId) {
  const res = await fetch(`${BASE_URL}/sessions/${sessionId}/transcript`);
  if (!res.ok) throw new Error("Transcript 불러오기 실패");
  return res.text();
}

/**
 * 세션별 오디오 목록 가져오기
 */
export async function fetchAudios(sessionId) {
  const res = await fetch(`${BASE_URL}/sessions/${sessionId}/audios`);
  if (!res.ok) throw new Error("오디오 파일 목록 불러오기 실패");
  return res.json();
}

/**
 * 구직 여부 업데이트 (PATCH 요청)
 */
export async function updateJobSeekingStatus(sessionId, newStatus) {
  const res = await fetch(`${BASE_URL}/sessions/${sessionId}/metadata`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ is_job_seeking: newStatus }),
  });

  if (!res.ok) throw new Error("구직 여부 업데이트 실패");
  return res.json();
}
