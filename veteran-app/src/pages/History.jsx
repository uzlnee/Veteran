import React, { useEffect, useState } from "react";
import "tailwindcss/tailwind.css";

// const BASE_URL = "";

const History = () => {
  const [sessions, setSessions] = useState([]);
  const [sessionUserMap, setSessionUserMap] = useState({});
  const [selectedSession, setSelectedSession] = useState(null);
  const [userData, setUserData] = useState(null);
  const [transcript, setTranscript] = useState("");
  const [audioFiles, setAudioFiles] = useState([]);
  const [showAudio, setShowAudio] = useState(false);
  const [loading, setLoading] = useState(false);

  // 검색/필터/정렬 상태
  const [searchName, setSearchName] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [sortOrder, setSortOrder] = useState("desc"); // 최신순: desc, 오래된순: asc

  // 세션 목록 불러오기
  useEffect(() => {
    const cachedSessions = localStorage.getItem("sessionList");
    if (cachedSessions) {
      const parsed = JSON.parse(cachedSessions);
      setSessions(parsed);
    } else {
      fetch("/api/sessions")
        .then((res) => res.json())
        .then((data) => {
          if (!Array.isArray(data)) throw new Error("Invalid sessions data");
          setSessions(data);
          localStorage.setItem("sessionList", JSON.stringify(data));
        })
        .catch((err) => console.error("세션 목록 불러오기 오류:", err));
    }
  }, []);

  // 각 세션의 메타데이터 미리 불러오기 (이름, 나이, 매칭여부 등)
  useEffect(() => {
    const fetchMeta = async () => {
      const map = {};
      await Promise.all(
        sessions.map(async (s) => {
          try {
            const res = await fetch(`/api/sessions/${s}/metadata`);
            if (res.ok) {
              const meta = await res.json();
              map[s] = meta;
            }
          } catch {}
        })
      );
      setSessionUserMap(map);
    };
    if (sessions.length > 0) fetchMeta();
  }, [sessions]);

  // 내역ID 클릭 시 상세정보 불러오기
  const handleSessionSelect = async (session) => {
    setSelectedSession(session);
    setLoading(true);
    setShowAudio(false);
    try {
      const [metaRes, transcriptRes, audioRes] = await Promise.all([
        fetch(`/api/sessions/${session}/metadata`),
        fetch(`/api/sessions/${session}/transcript`),
        fetch(`/api/sessions/${session}/audios`),
      ]);
      if (metaRes.ok) setUserData(await metaRes.json());
      else setUserData(null);
      if (transcriptRes.ok) setTranscript(await transcriptRes.text());
      else setTranscript("");
      if (audioRes.ok) setAudioFiles(await audioRes.json());
      else setAudioFiles([]);
    } catch (err) {
      setUserData(null);
      setTranscript("");
      setAudioFiles([]);
    } finally {
      setLoading(false);
    }
  };

  // 파일 다운로드
  const downloadFile = (filename) => {
    const link = document.createElement("a");
    link.href = `/recordings/${selectedSession}/${filename}`;
    link.download = filename;
    link.click();
  };

  // 테이블에 표시할 데이터 가공 및 필터/정렬
  let tableRows = sessions.map((s, idx) => {
    const meta = sessionUserMap[s] || {};
    const id = `HIS${String(idx + 1).padStart(3, "0")}`;
    const date = `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}`;
    const time = `${s.slice(9, 11)}:${s.slice(11, 13)}:${s.slice(13, 15)}`;
    const name = meta.name || "-";
    const age = meta.age || "-";
    const matched = meta.is_job_seeking === undefined ? null : meta.is_job_seeking;
    return { id, session: s, date, time, name, age, matched, dateRaw: s.slice(0, 8) };
  });

  // 이름 검색 필터
  if (searchName.trim() !== "") {
    tableRows = tableRows.filter((row) => row.name.includes(searchName.trim()));
  }
  // 날짜 필터
  if (startDate) {
    const startKey = startDate.replace(/-/g, "");
    tableRows = tableRows.filter((row) => row.dateRaw >= startKey);
  }
  if (endDate) {
    const endKey = endDate.replace(/-/g, "");
    tableRows = tableRows.filter((row) => row.dateRaw <= endKey);
  }
  // 정렬
  tableRows.sort((a, b) => {
    if (sortOrder === "desc") {
      if (b.dateRaw === a.dateRaw) {
        // 시간 내림차순
        return b.time.localeCompare(a.time);
      }
      return b.dateRaw.localeCompare(a.dateRaw);
    } else {
      if (a.dateRaw === b.dateRaw) {
        // 시간 오름차순
        return a.time.localeCompare(b.time);
      }
      return a.dateRaw.localeCompare(b.dateRaw);
    }
  });

  return (
    <div className="font-pre min-h-screen bg-gray-50">
      <div className="bg-blue-500 px-6 py-4">
        <h2 className="text-xl font-semibold text-white tracking-widest">HISTORY</h2>
      </div>
      {/* 상단 검색/필터/정렬 UI */}
      <div className="flex flex-col md:flex-row gap-3 md:gap-4 items-center px-6 pt-6 pb-2">
        <input
          type="text"
          className="border rounded px-4 py-2 w-full md:w-60"
          placeholder="이름으로 검색..."
          value={searchName}
          onChange={e => setSearchName(e.target.value)}
        />
        <input
          type="date"
          className="border rounded px-4 py-2 w-full md:w-44"
          value={startDate}
          onChange={e => setStartDate(e.target.value)}
        />
        <span className="mx-1">~</span>
        <input
          type="date"
          className="border rounded px-4 py-2 w-full md:w-44"
          value={endDate}
          onChange={e => setEndDate(e.target.value)}
        />
        <select
          className="border rounded px-4 py-2 w-full md:w-32"
          value={sortOrder}
          onChange={e => setSortOrder(e.target.value)}
        >
          <option value="desc">최신순</option>
          <option value="asc">오래된순</option>
        </select>
      </div>
      <div className="p-6 flex flex-col gap-6">
        <div className="bg-white rounded shadow-md p-6 w-full border">
          <h3 className="text-base font-semibold mb-4">상담 내역</h3>
          <div className="overflow-y-auto max-h-[400px]">
            <table className="min-w-full text-sm border">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border px-4 py-2">내역 ID</th>
                  <th className="border px-4 py-2">상담일자</th>
                  <th className="border px-4 py-2">상담시간</th>
                  <th className="border px-4 py-2">이름</th>
                  <th className="border px-4 py-2">나이</th>
                  <th className="border px-4 py-2">매칭 여부</th>
                </tr>
              </thead>
              <tbody>
                {tableRows.map((row) => (
                  <tr key={row.session} className="hover:bg-blue-50">
                    <td className="border px-4 py-2 text-blue-700 underline cursor-pointer" onClick={() => handleSessionSelect(row.session)}>{row.id}</td>
                    <td className="border px-4 py-2">{row.date}</td>
                    <td className="border px-4 py-2">{row.time}</td>
                    <td className="border px-4 py-2">{row.name}</td>
                    <td className="border px-4 py-2">{row.age}</td>
                    <td className="border px-4 py-2">
                      {row.matched === null ? (
                        <span className="inline-block px-3 py-1 rounded bg-gray-200 text-gray-600">-</span>
                      ) : row.matched ? (
                        <span className="inline-block px-3 py-1 rounded bg-green-200 text-green-700 font-semibold">Yes</span>
                      ) : (
                        <span className="inline-block px-3 py-1 rounded bg-red-200 text-red-700 font-semibold">No</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {selectedSession && userData && (
          <div className="space-y-6">
            {loading && <p className="text-gray-600">불러오는 중...</p>}
            {!loading && (
              <>
                <div className="bg-white p-6 rounded shadow-md border">
                  <div className="text-lg font-bold mb-4 text-gray-800">{userData.name}</div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                      <tbody className="divide-y divide-gray-200">
                        <tr><td className="font-semibold text-gray-700 py-2 pr-4">나이</td><td className="py-2">{userData.age}</td></tr>
                        <tr><td className="font-semibold text-gray-700 py-2 pr-4">거주지</td><td className="py-2">{userData.location}</td></tr>
                        <tr><td className="font-semibold text-gray-700 py-2 pr-4">희망시간대</td><td className="py-2">{userData.available_time}</td></tr>
                        <tr><td className="font-semibold text-gray-700 py-2 pr-4">자격증</td><td className="py-2">{userData.license}</td></tr>
                        <tr><td className="font-semibold text-gray-700 py-2 pr-4">희망분야</td><td className="py-2">{userData.preferred_field}</td></tr>
                        <tr><td className="font-semibold text-gray-700 py-2 pr-4">건강상태</td><td className="py-2">{userData.health_condition}</td></tr>
                        <tr><td className="font-semibold text-gray-700 py-2 pr-4">경력</td><td className="py-2">{userData.carrer}</td></tr>
                        <tr><td className="font-semibold text-gray-700 py-2 pr-4">학력</td><td className="py-2">{userData.education}</td></tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                <div className="bg-white p-6 rounded shadow-md border">
                  <h4 className="text-base font-bold mb-4 text-gray-800">📝 상담 대화</h4>
                  <div className="whitespace-pre-wrap bg-gray-100 p-4 rounded text-sm border text-gray-800">
                    {transcript}
                  </div>
                </div>
                <div className="bg-white p-6 rounded shadow-md border">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-base font-bold text-gray-800">🔊 상담 녹음파일</h4>
                    <button
                      onClick={() => setShowAudio(!showAudio)}
                      className="text-sm text-blue-500 hover:underline"
                    >
                      {showAudio ? "접기" : "펼치기"}
                    </button>
                  </div>
                  {showAudio && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {audioFiles.map((f) => (
                        <div key={f}>
                          <audio controls src={`/recordings/${selectedSession}/${f}`} className="w-full" />
                          <div className="flex justify-between items-center mt-1">
                            <p className="text-sm text-gray-700 truncate mr-2">{f}</p>
                            <button
                              className="text-xs text-blue-600 hover:underline"
                              onClick={() => downloadFile(f)}
                            >
                              다운로드
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default History;