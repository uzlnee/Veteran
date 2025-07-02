// src/pages/JobDetail.jsx
import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '../components/button'

export default function JobDetail() {
  const { filename } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [expandedIndex, setExpandedIndex] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`/api/jobs/${filename}`)
        if (!res.ok) throw new Error("데이터 없음")
        const json = await res.json()
        setData(json)
      } catch {
        setData(null)
      }
    }
    fetchData()
  }, [filename])

  if (!data) return <div className="p-6">불러오는 중 또는 데이터가 없습니다.</div>

  return (
    <div className="relative p-6">
      {/* 오른쪽 상단 뒤로가기 버튼 */}
      <div className="absolute top-4 right-4">
        <Button
          onClick={() => navigate(-1)}
          variant="outline"
          size="sm"
          className="shadow border-gray-300 hover:bg-gray-100"
        >
          돌아가기
        </Button>
      </div>

      <h1 className="text-2xl font-bold mb-2">{data.jobSeeker?.name}님의 추천 직업 상세</h1>
      <p className="text-gray-600 mb-4">
        생성일: {new Date(data.generatedAt).toLocaleDateString()}
      </p>

      {/* 기본 정보 카드 */}
      <div className="bg-white border rounded-lg shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-2">기본 정보</h2>
        <ul className="text-sm text-gray-700 space-y-1">
          <li><strong>나이:</strong> {data.jobSeeker?.age}세</li>
          <li><strong>거주지:</strong> {data.jobSeeker?.location}</li>
          <li><strong>가능 시간:</strong> {data.jobSeeker?.available_time || data.jobSeeker?.availableTime}</li>
          <li><strong>자격증:</strong> {(data.jobSeeker?.license || data.jobSeeker?.licenses)?.join(', ') || '없음'}</li>
          <li><strong>희망 분야:</strong> {(data.jobSeeker?.preferred_field || data.jobSeeker?.preferredFields)?.join(', ') || '없음'}</li>
          <li><strong>건강 상태:</strong> {data.jobSeeker?.health_condition || data.jobSeeker?.healthCondition}</li>
          <li><strong>학력:</strong> {data.jobSeeker?.education}</li>
          <li><strong>경력:</strong> {Array.isArray(data.jobSeeker?.career)
            ? data.jobSeeker.career.map(c => `${c.org} (${c.years}년)`).join(', ')
            : data.jobSeeker?.career || '없음'}
          </li>
        </ul>
      </div>

      {/* 추천 일자리 목록 */}
      <h2 className="text-xl font-semibold mt-4 mb-2">추천 일자리 목록</h2>
      <ul className="space-y-4">
        {data.recommendations
          .filter(rec => rec.jobPosting)
          .map((rec, i) => {
            const { jobPosting, unifiedScore, reason } = rec

            // 점수 분류
            let tag = '검토 필요'
            let scoreClass = 'bg-gray-200 text-gray-800'
            if (unifiedScore >= 0.35) {
              tag = '적합'
              scoreClass = 'bg-blue-100 text-blue-800'
            } else if (unifiedScore < 0.25) {
              tag = '부적합'
              scoreClass = 'bg-red-100 text-red-800'
            }

            return (
              <li key={i} className="p-4 border rounded-md bg-white shadow-sm">
                <div className="flex justify-between items-center mb-1">
                  <p className="font-semibold text-base">{jobPosting.title}</p>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${scoreClass}`}>
                    {tag} ({(unifiedScore * 100).toFixed(1)}점)
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-1">
                  {jobPosting.company} | 거리: {jobPosting.distanceKm?.toFixed(2)}km
                </p>
                <p className="text-sm text-gray-500 mb-2">
                📍 {jobPosting.address}
                </p>
                <p className="text-sm text-gray-800 leading-relaxed">
                  {expandedIndex === i ? reason : reason.split('.')[0] + '.'}
                  {reason.split('.').length > 1 && (
                    <button
                      className="ml-2 text-blue-600 text-xs underline"
                      onClick={() => setExpandedIndex(expandedIndex === i ? null : i)}
                    >
                      {expandedIndex === i ? '간략히' : '자세히'}
                    </button>
                  )}
                </p>
              </li>
            )
          })}
      </ul>
    </div>
  )
}
