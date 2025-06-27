// import React, { useEffect, useState } from "react";
// import Calendar from "react-calendar";
// import "react-calendar/dist/Calendar.css";
// import "tailwindcss/tailwind.css";

// const History = () => {
//   const [sessions, setSessions] = useState([]);
//   const [dateMap, setDateMap] = useState({});
//   const [selectedDate, setSelectedDate] = useState(null);
//   const [filteredSessions, setFilteredSessions] = useState([]);
//   const [selectedSession, setSelectedSession] = useState(null);
//   const [userData, setUserData] = useState(null);
//   const [transcript, setTranscript] = useState("");
//   const [audioFiles, setAudioFiles] = useState([]);
//   const [showAudio, setShowAudio] = useState(false);

//   useEffect(() => {
//     fetch("http://localhost:5050/api/sessions")
//       .then((res) => res.json())
//       .then((data) => {
//         if (!Array.isArray(data)) {
//           console.error("API 응답이 배열이 아닙니다:", data);
//           return;
//         }
//         setSessions(data);
  
//         const map = {};
//         data.forEach((s) => {
//           const dateKey = s.slice(0, 8);
//           if (!map[dateKey]) map[dateKey] = [];
//           map[dateKey].push(s);
//         });
//         setDateMap(map);
//       })
//       .catch((err) => {
//         console.error("세션 목록 불러오기 오류:", err);
//       });
//   }, []);
  

//   const handleDateChange = (date) => {
//     const key = date.toISOString().slice(0, 10).replace(/-/g, "");
//     setSelectedDate(key);
//     setSelectedSession(null);
//     setUserData(null);
//     setTranscript("");
//     setAudioFiles([]);
//     setFilteredSessions(dateMap[key] || []);
//   };

//   const handleSessionSelect = async (session) => {
//     setSelectedSession(session);
//     try {
//       const [metaRes, transcriptRes, audioRes] = await Promise.all([
//         fetch(`http://localhost:5050/api/sessions/${session}/metadata`),
//         fetch(`http://localhost:5050/api/sessions/${session}/transcript`),
//         fetch(`http://localhost:5050/api/sessions/${session}/audios`),
//       ]);

//       if (metaRes.ok) setUserData(await metaRes.json());
//       else setUserData(null);

//       if (transcriptRes.ok) setTranscript(await transcriptRes.text());
//       else setTranscript("");

//       if (audioRes.ok) setAudioFiles(await audioRes.json());
//       else setAudioFiles([]);
//     } catch (err) {
//       console.error("Error loading session data:", err);
//     }
//   };

//   return (
//     <div className="font-pre">
//       <div className="min-h-screen bg-gray-50">
//         <div className="bg-blue-500 px-6 py-4">
//           <h2 className="text-xl font-semibold text-white">HISTORY</h2>
//         </div>

//         <div className="p-6 flex flex-col lg:flex-row gap-6">
//           <div className="bg-white rounded shadow-md p-4 w-full lg:w-[360px] h-[360px] border overflow-hidden">
//             <Calendar
//               onChange={handleDateChange}
//               tileContent={({ date }) => {
//                 const key = date.toISOString().slice(0, 10).replace(/-/g, "");
//                 const count = dateMap[key]?.length || 0;
//                 return count > 0 ? (
//                   <div className="text-[10px] text-orange-500 text-center mt-1">● {count}</div>
//                 ) : null;
//               }}
//               formatDay={(_, date) => date.getDate()}
//               calendarType="gregory"
//               className="react-calendar border-none text-center w-full h-full"
//             />
//           </div>

//           {filteredSessions.length > 0 && (
//             <div className="bg-white rounded shadow-md p-6 w-full lg:flex-1 border max-h-[360px] overflow-y-auto">
//               <h3 className="text-base font-semibold mb-4">📋 상담 내역</h3>
//               <div className="space-y-4">
//                 {filteredSessions.map((s, idx) => (
//                   <div
//                     key={s}
//                     className="flex items-center justify-between bg-gray-100 hover:bg-gray-200 p-4 rounded cursor-pointer shadow-sm"
//                     onClick={() => handleSessionSelect(s)}
//                   >
//                     <div className="flex items-center space-x-4">
//                       <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center font-bold text-white text-sm">
//                         {String(idx + 1).padStart(3, "0")}
//                       </div>
//                       <div>
//                         <div className="font-bold text-blue-700">사용자 ID: USER_{String(idx + 1).padStart(3, "0")}</div>
//                         <div className="text-gray-700 text-sm">이름: {userData?.name || "-"}</div>
//                       </div>
//                     </div>
//                     <div className="text-right text-sm text-gray-600">
//                       <div>상담일자: {`${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)} ${s.slice(9, 11)}:${s.slice(11, 13)}`}</div>
//                       <div>구직여부: {userData?.is_job_seeking ? "예" : "아니오"}</div>
//                     </div>
//                   </div>
//                 ))}
//               </div>
//             </div>
//           )}
//         </div>

//         {selectedSession && userData && (
//           <div className="p-6 space-y-6">
//             <div className="bg-white p-6 rounded shadow-md border">
//               <div className="text-lg font-bold mb-4 text-gray-800">{userData.name}</div>
//               <div className="overflow-x-auto">
//                 <table className="min-w-full text-sm">
//                   <tbody className="divide-y divide-gray-200">
//                     <tr><td className="font-semibold text-gray-700 py-2 pr-4">나이</td><td className="py-2">{userData.age}</td></tr>
//                     <tr><td className="font-semibold text-gray-700 py-2 pr-4">거주지</td><td className="py-2">{userData.location}</td></tr>
//                     <tr><td className="font-semibold text-gray-700 py-2 pr-4">희망시간대</td><td className="py-2">{userData.available_time}</td></tr>
//                     <tr><td className="font-semibold text-gray-700 py-2 pr-4">자격증</td><td className="py-2">{userData.license}</td></tr>
//                     <tr><td className="font-semibold text-gray-700 py-2 pr-4">희망분야</td><td className="py-2">{userData.preferred_field}</td></tr>
//                     <tr><td className="font-semibold text-gray-700 py-2 pr-4">건강상태</td><td className="py-2">{userData.health_condition}</td></tr>
//                     <tr><td className="font-semibold text-gray-700 py-2 pr-4">경력</td><td className="py-2">{userData.carrer}</td></tr>
//                     <tr><td className="font-semibold text-gray-700 py-2 pr-4">학력</td><td className="py-2">{userData.education}</td></tr>
//                   </tbody>
//                 </table>
//               </div>
//             </div>

//             <div className="bg-white p-6 rounded shadow-md border">
//               <h4 className="text-base font-bold mb-4 text-gray-800">📝 상담 대화</h4>
//               <div className="whitespace-pre-wrap bg-gray-100 p-4 rounded text-sm border text-gray-800">
//                 {transcript}
//               </div>
//             </div>

//             <div className="bg-white p-6 rounded shadow-md border">
//               <div className="flex items-center justify-between mb-4">
//                 <h4 className="text-base font-bold text-gray-800">🔊 상담 녹음파일</h4>
//                 <button
//                   onClick={() => setShowAudio(!showAudio)}
//                   className="text-sm text-blue-500 hover:underline"
//                 >
//                   {showAudio ? "접기" : "펼치기"}
//                 </button>
//               </div>
//               {showAudio && (
//                 <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
//                   {audioFiles.map((f) => (
//                     <div key={f}>
//                       <audio controls src={`http://localhost:5050/recordings/${selectedSession}/${f}`} className="w-full" />
//                       <p className="text-sm mt-1 text-gray-700">{f}</p>
//                     </div>
//                   ))}
//                 </div>
//               )}
//             </div>
//           </div>
//         )}
//       </div>
//     </div>
//   );
// };

// export default History;

import React, { useEffect, useState } from "react";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";
import "tailwindcss/tailwind.css";

const History = () => {
  const [sessions, setSessions] = useState([]);
  const [dateMap, setDateMap] = useState({});
  const [selectedDate, setSelectedDate] = useState(null);
  const [filteredSessions, setFilteredSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [userData, setUserData] = useState(null);
  const [sessionUserMap, setSessionUserMap] = useState({});
  const [transcript, setTranscript] = useState("");
  const [audioFiles, setAudioFiles] = useState([]);
  const [showAudio, setShowAudio] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const cachedSessions = localStorage.getItem("sessionList");
    if (cachedSessions) {
      const parsed = JSON.parse(cachedSessions);
      setSessions(parsed);
      const map = {};
      parsed.forEach((s) => {
        const dateKey = s.slice(0, 8);
        if (!map[dateKey]) map[dateKey] = [];
        map[dateKey].push(s);
      });
      setDateMap(map);
    } else {
      fetch("http://localhost:5050/api/sessions")
        .then((res) => res.json())
        .then((data) => {
          if (!Array.isArray(data)) throw new Error("Invalid sessions data");
          setSessions(data);
          localStorage.setItem("sessionList", JSON.stringify(data));
          const map = {};
          data.forEach((s) => {
            const dateKey = s.slice(0, 8);
            if (!map[dateKey]) map[dateKey] = [];
            map[dateKey].push(s);
          });
          setDateMap(map);
        })
        .catch((err) => console.error("세션 목록 불러오기 오류:", err));
    }
  }, []);

  const handleDateChange = (date) => {
    const key = date.toISOString().slice(0, 10).replace(/-/g, "");
    setSelectedDate(key);
    setSelectedSession(null);
    setUserData(null);
    setTranscript("");
    setAudioFiles([]);
    setFilteredSessions(dateMap[key] || []);
  };

  const handleSessionSelect = async (session) => {
    setSelectedSession(session);
    setLoading(true);
    try {
      const [metaRes, transcriptRes, audioRes] = await Promise.all([
        fetch(`http://localhost:5050/api/sessions/${session}/metadata`),
        fetch(`http://localhost:5050/api/sessions/${session}/transcript`),
        fetch(`http://localhost:5050/api/sessions/${session}/audios`),
      ]);

      if (metaRes.ok) {
        const meta = await metaRes.json();
        setUserData(meta);
        setSessionUserMap((prev) => ({ ...prev, [session]: meta }));
      } else setUserData(null);

      if (transcriptRes.ok) setTranscript(await transcriptRes.text());
      else setTranscript("");

      if (audioRes.ok) setAudioFiles(await audioRes.json());
      else setAudioFiles([]);
    } catch (err) {
      console.error("Error loading session data:", err);
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = (filename) => {
    const link = document.createElement("a");
    link.href = `http://localhost:5050/recordings/${selectedSession}/${filename}`;
    link.download = filename;
    link.click();
  };

  return (
    <div className="font-pre min-h-screen bg-gray-50">
      <div className="bg-blue-500 px-6 py-4">
        <h2 className="text-xl font-semibold text-white">HISTORY</h2>
      </div>

      <div className="p-6 flex flex-col lg:flex-row gap-6">
        <div className="bg-white rounded shadow-md p-4 w-full lg:w-[360px] h-[360px] border overflow-hidden">
          <Calendar
            onChange={handleDateChange}
            tileContent={({ date }) => {
              const key = date.toISOString().slice(0, 10).replace(/-/g, "");
              const count = dateMap[key]?.length || 0;
              return count > 0 ? (
                <div className="text-[10px] text-orange-500 text-center mt-1">● {count}</div>
              ) : null;
            }}
            formatDay={(_, date) => date.getDate()}
            calendarType="gregory"
            className="react-calendar border-none text-center w-full h-full"
          />
        </div>

        {filteredSessions.length > 0 && (
          <div className="bg-white rounded shadow-md p-6 w-full lg:flex-1 border max-h-[360px] overflow-y-auto">
            <h3 className="text-base font-semibold mb-4">📋 상담 내역</h3>
            <div className="space-y-4">
              {filteredSessions.map((s, idx) => (
                <div
                  key={s}
                  className="flex items-center justify-between bg-gray-100 hover:bg-gray-200 p-4 rounded cursor-pointer shadow-sm"
                  onClick={() => handleSessionSelect(s)}
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center font-bold text-white text-sm">
                      {String(idx + 1).padStart(3, "0")}
                    </div>
                    <div>
                      <div className="font-bold text-blue-700">사용자 ID: USER_{String(idx + 1).padStart(3, "0")}</div>
                      <div className="text-gray-700 text-sm">
                        이름: {sessionUserMap[s]?.name || "-"}
                      </div>
                    </div>
                  </div>
                  <div className="text-right text-sm text-gray-600">
                    <div>상담일자: {`${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)} ${s.slice(9, 11)}:${s.slice(11, 13)}`}</div>
                    <div>구직여부: {sessionUserMap[s]?.is_job_seeking ? "예" : "아니오"}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {selectedSession && userData && (
        <div className="p-6 space-y-6">
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
                        <audio controls src={`http://localhost:5050/recordings/${selectedSession}/${f}`} className="w-full" />
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
  );
};

export default History;
