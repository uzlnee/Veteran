// import { useEffect, useState } from 'react';

// export default function JobRecommendation() {
//   const [data, setData] = useState(null);
//   const [selectedTab, setSelectedTab] = useState(0);

//   useEffect(() => {
//     fetch('public/data/김옥자_20250515.json') // public 폴더 기준 경로
//       .then((res) => res.json())
//       .then((json) => setData(json))
//       .catch((err) => console.error('JSON 로딩 오류:', err));
//   }, []);

//   if (!data) {
//     return <div className="p-4">추천 결과를 불러오는 중입니다...</div>;
//   }

//   const user = data.jobSeeker || {};
//   const recommendations = data.recommendations || [];

//   const formatDate = (isoString) => {
//     try {
//       const date = new Date(isoString);
//       return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일 ${date.getHours()}시 ${date.getMinutes()}분`;
//     } catch {
//       return isoString;
//     }
//   };

//   return (
//     <div className="p-6 max-w-5xl mx-auto">
//       <h1 className="text-2xl font-bold mb-4">💼 일자리 추천 결과</h1>
//       <h2 className="text-xl font-semibold mb-1">{user.name || '알 수 없음'}님의 추천 결과</h2>
//       {data.generatedAt && (
//         <p className="text-sm text-gray-500 mb-4">생성일시: {formatDate(data.generatedAt)}</p>
//       )}

//       {/* 구직자 정보 */}
//       <div className="bg-gray-50 p-4 rounded-lg shadow mb-6">
//         <h3 className="font-bold mb-2">👤 구직자 정보</h3>
//         <div className="grid grid-cols-2 gap-4">
//           <div>
//             <p>이름: {user.name || '-'}</p>
//             <p>나이: {user.age || '-'}세</p>
//             <p>희망 지역: {user.location || '-'}</p>
//             <p>가능 시간: {user.availableTime || '-'}</p>
//           </div>
//           <div>
//             <p>보유 자격증: {(user.licenses || ['-']).join(', ')}</p>
//             <p>희망 분야: {(user.preferredFields || ['-']).join(', ')}</p>
//             <p>건강 상태: {user.healthCondition || '-'}</p>
//             <p>학력: {user.education || '-'}</p>
//           </div>
//         </div>
//         {user.career && (
//           <div className="mt-4">
//             <p>경력:</p>
//             <ul className="list-disc ml-5">
//               {user.career.map((c, idx) => (
//                 <li key={idx}>{c.org} {c.title} {c.years}년</li>
//               ))}
//             </ul>
//           </div>
//         )}
//       </div>

//       {/* 추천 직업 목록 */}
//       {recommendations.length > 0 ? (
//         <div>
//           <h3 className="text-xl font-bold mb-4">📋 추천 직업 목록</h3>
//           <div className="flex flex-wrap gap-2 mb-4">
//             {recommendations.map((rec, i) => (
//               <button
//                 key={i}
//                 className={`px-4 py-2 rounded ${selectedTab === i ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
//                 onClick={() => setSelectedTab(i)}
//               >
//                 {i + 1}순위: {rec.occupation?.title || '정보 없음'}
//               </button>
//             ))}
//           </div>

//           {/* 선택된 직업 상세 정보 */}
//           <div className="bg-white p-4 rounded shadow">
//             <h4 className="text-lg font-semibold mb-2">
//               {recommendations[selectedTab].occupation?.title || '정보 없음'}
//             </h4>
//             <p>직업 분류: {recommendations[selectedTab].occupation?.category || '-'}</p>
//             <p>추천 이유: {recommendations[selectedTab].occupation?.reason || '-'}</p>
//             <p>직업 코드: {recommendations[selectedTab].occupation?.code || '-'}</p>

//             <details className="mt-2">
//               <summary className="cursor-pointer font-semibold">직업 상세 정보</summary>
//               <div className="mt-2 space-y-1">
//                 <p>요약: {recommendations[selectedTab].occupation?.summary || '-'}</p>
//                 <p>하는 일:</p>
//                 <ul className="list-disc ml-5">
//                   {(recommendations[selectedTab].occupation?.tasks || []).map((task, i) => (
//                     <li key={i}>{task}</li>
//                   ))}
//                 </ul>
//                 <p>되는 길: {recommendations[selectedTab].occupation?.careerPath || '-'}</p>
//               </div>
//             </details>

//             {/* 구인 정보 */}
//             <div className="mt-4">
//               <h5 className="font-semibold mb-1">📢 구인 정보</h5>
//               {recommendations[selectedTab].jobPostings?.length ? (
//                 recommendations[selectedTab].jobPostings.map((post, j) => (
//                   <details key={j} className="border p-2 rounded mb-2">
//                     <summary className="font-medium cursor-pointer">{post.title}</summary>
//                     <div className="mt-2 space-y-1">
//                       <p>사업장명: {post.company}</p>
//                       <p>사업장주소: {post.address}</p>
//                       {post.distanceKm && <p>거리: {post.distanceKm}km</p>}
//                       <p>연령: {post.ageLimit}</p>
//                       {post.applicationPeriod && (
//                         <p>접수기간: {post.applicationPeriod.from || '-'} ~ {post.applicationPeriod.to || '-'}</p>
//                       )}
//                       {post.applyMethod && <p>접수방법: {post.applyMethod}</p>}
//                       {post.contact && <p>담당자연락처: {post.contact}</p>}
//                       {post.homepage && <p>홈페이지: {post.homepage}</p>}
//                       {post.details && <p>상세 내용: {post.details}</p>}
//                     </div>
//                   </details>
//                 ))
//               ) : (
//                 <p className="text-gray-500">현재 구인 정보가 없습니다.</p>
//               )}
//             </div>
//           </div>
//         </div>
//       ) : (
//         <p className="text-red-500">추천 직업 정보가 없습니다.</p>
//       )}
//     </div>
//   );
// }

// import React, { useEffect, useState } from "react";
// import "tailwindcss/tailwind.css";

// const Jobs = () => {
//   const [recommendations, setRecommendations] = useState([]);

//   useEffect(() => {
//     // 로컬 서버에서 추천 JSON 파일 목록을 가져옴
//     fetch("http://localhost:5050/api/recommendations")
//       .then((res) => res.json())
//       .then((data) => {
//         const allRecs = [];

//         Promise.all(
//           data.map((filename) =>
//             fetch(`http://localhost:5050/api/recommendations/${filename}`)
//               .then((res) => res.json())
//               .then((json) => allRecs.push(json))
//           )
//         ).then(() => setRecommendations(allRecs));
//       })
//       .catch((err) => console.error("추천 파일 로딩 오류:", err));
//   }, []);

//   return (
//     <div className="font-pre min-h-screen bg-gray-50 p-6">
//       <h2 className="text-2xl font-bold text-blue-800 mb-6">👥 사용자별 일자리 추천</h2>
//       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
//         {recommendations.map((rec, idx) => (
//           <div
//             key={idx}
//             className="bg-white p-6 rounded-lg shadow-md border border-gray-200"
//           >
//             <h3 className="text-xl font-semibold text-blue-600 mb-2">
//               {rec.name} 님의 추천 직무
//             </h3>
//             <div className="space-y-4">
//               {rec.recommendations.map((item, index) => (
//                 <div key={index} className="border rounded p-4 bg-gray-50">
//                   <h4 className="font-bold text-gray-800">{item.occupation}</h4>
//                   <ul className="list-disc ml-5 mt-2 text-sm text-gray-700 space-y-1">
//                     {item.jobPostings.map((job, i) => (
//                       <li key={i}>{job}</li>
//                     ))}
//                   </ul>
//                 </div>
//               ))}
//             </div>
//           </div>
//         ))}
//       </div>
//     </div>
//   );
// };
// export default Jobs;

// 새로운 프론트엔드
// src/pages/Jobs.jsx
/* eslint-disable no-undef */

import React, { useEffect, useState } from 'react'
import { Card, CardContent } from '../components/JobCard.jsx'
import { Button } from '../components/button'
import { ScrollArea } from '../components/scroll-area'
import { format } from 'date-fns'
import { useNavigate } from 'react-router-dom'

export default function Jobs() {
  const [jobData, setJobData] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [sortOrder, setSortOrder] = useState('desc')
  const navigate = useNavigate()

  useEffect(() => {
    const filenames = [
      '김구인_20250627.json',
      '김승일_20250627.json',
      '김옥자_20250515.json',
      '김옥희_20250515.json',
      '박춘배_20250515.json',
      '유영희_20250629.json',
      '박춘배_20250627.json',
      '이순희_20250515.json'
    ]

    const fetchData = async () => {
      const allData = await Promise.all(
        filenames.map(name =>
          fetch(`/data/${name}`).then(res => res.json())
        )
      )

      const parsed = allData.map(file => ({
        name: file.jobSeeker?.name,
        created: new Date(file.generatedAt.split('T')[0]),
        recommendations: file.recommendations || []
      }))

      setJobData(parsed)
    }

    fetchData()
  }, [])

  const filteredData = jobData
    .filter(d => {
      const nameMatch = d.name.toLowerCase().includes(searchTerm.toLowerCase())
      const createdTime = new Date(d.created).getTime()
      const startOk = startDate ? createdTime >= new Date(startDate).getTime() : true
      const endOk = endDate ? createdTime <= new Date(endDate).getTime() : true
      return nameMatch && startOk && endOk
    })
    .sort((a, b) => {
      return sortOrder === 'asc' ? a.created - b.created : b.created - a.created
    })

  return (
    <div className="flex flex-col min-h-screen bg-gray-50 font-pre">
      {/* 상단 파란 헤더 (다른 페이지와 동일) */}
      <div className="bg-blue-500 px-6 py-4">
        <h2 className="text-xl font-semibold text-white tracking-widest">JOBS</h2>
      </div>
      {/* 검색창 */}
      <div className="bg-white px-6 py-4 shadow-sm border-b flex flex-col md:flex-row flex-wrap gap-4 items-start md:items-center">
        <input
          type="text"
          placeholder="이름으로 검색..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          className="w-full md:w-60 px-4 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <div className="flex items-center gap-2">
          <input
            type="date"
            value={startDate}
            onChange={e => setStartDate(e.target.value)}
            className="w-full md:w-48 px-4 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <span className="text-gray-500">~</span>
          <input
            type="date"
            value={endDate}
            onChange={e => setEndDate(e.target.value)}
            className="w-full md:w-48 px-4 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>
        <select
          value={sortOrder}
          onChange={e => setSortOrder(e.target.value)}
          className="w-full md:w-40 px-4 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option value="desc">최신순</option>
          <option value="asc">오래된순</option>
        </select>
      </div>
      {/* 본문 컨텐츠 */}
      <main className="flex-1 overflow-y-auto p-6 bg-gray-50">
        <ScrollArea className="h-full pr-2">
          {filteredData.length === 0 ? (
            <div className="text-center text-gray-500 mt-20 text-lg">
              검색 결과가 없습니다.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {filteredData.map(({ name, created, recommendations }, idx) => (
                <Card key={idx} className="hover:shadow-xl transition-shadow">
                  <CardContent className="p-4">
                    <div className="text-sm text-gray-500">
                      생성일: {format(created, 'yyyy-MM-dd')}
                    </div>
                    <h2 className="text-xl font-semibold mt-2">{name}님을 위한 추천</h2>
                    <ul className="mt-2 list-disc pl-4 text-sm text-gray-700">
                      {recommendations.slice(0, 3).map((rec, i) => (
                        <li key={i}>
                          <span className="font-medium">{rec.jobPosting?.title}</span> - {rec.jobPosting?.company}
                        </li>
                      ))}
                    </ul>
                    <div className="mt-4 text-right">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/jobs/${encodeURIComponent(name)}`)}
                      >
                        자세히 보기
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </ScrollArea>
      </main>
    </div>
  )
}
