// src/pages/Jobs.jsx
import React, { useEffect, useState } from 'react'
import { Card, CardContent } from '../components/JobCard.jsx'
import { Button } from '../components/button'
import { ScrollArea } from '../components/scroll-area'
import { format } from 'date-fns'
import { useNavigate } from 'react-router-dom'
import { getJobFiles } from '../api/jobs'

export default function Jobs() {
  const [jobData, setJobData] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [sortOrder, setSortOrder] = useState('desc')
  const navigate = useNavigate()

  useEffect(() => {
    const fetchData = async () => {
      const filenames = await getJobFiles();

      const allData = await Promise.all(
        filenames.map(name =>
          fetch(`/api/jobs/${name}`).then(res => res.json().then(data => ({ ...data, filename: name })))
        )
      )

      const parsed = allData.map(file => ({
        name: file.jobSeeker?.name,
        created: new Date(file.generatedAt.split('T')[0]),
        recommendations: file.recommendations || [],
        filename: file.filename
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
              {filteredData.map(({ name, created, recommendations, filename }, idx) => (
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
                        onClick={() => navigate(`/jobs/${encodeURIComponent(filename)}`)}
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
