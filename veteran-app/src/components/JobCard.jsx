import React from "react";

const JobCard = ({ job }) => {
  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-lg font-bold">{job.title}</h2>
      <p className="text-sm text-gray-600">{job.company}</p>
      <p className="mt-1 text-sm">{job.description}</p>
      <p className="mt-2 text-sm text-blue-500">매칭 점수: {job.match_score}</p>
    </div>
  );
};

export default JobCard;
