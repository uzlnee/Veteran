// // CardStat.jsx
// import React from "react";
// import { FaArrowUp, FaArrowDown } from "react-icons/fa";

// const CardStat = ({ title, value, change, icon, color = "blue" }) => {
//   const isPositive = change >= 0;
//   return (
//     <div className="bg-white rounded-lg p-4 shadow-md flex justify-between items-center">
//       <div>
//         <h2 className="text-sm font-semibold text-gray-500 uppercase">{title}</h2>
//         <p className="text-2xl font-bold text-gray-800">{value}</p>
//         <p className={`text-sm mt-1 flex items-center ${isPositive ? "text-green-500" : "text-red-500"}`}>
//           {isPositive ? <FaArrowUp className="mr-1" /> : <FaArrowDown className="mr-1" />}
//           {Math.abs(change)}% Since last week
//         </p>
//       </div>
//       <div className={`bg-${color}-500 text-white p-3 rounded-full text-xl`}>{icon}</div>
//     </div>
//   );
// };

// export default CardStat;

// CardStat.jsx
import React from "react";
import { FaArrowUp, FaArrowDown } from "react-icons/fa";

const CardStat = ({ title, value, change, icon, color = "blue" }) => {
  const isPositive = change >= 0;
  return (
    <div className="bg-white rounded-lg p-4 shadow-md flex justify-between items-center">
      <div>
        <h2 className="text-sm font-semibold text-gray-500 uppercase">{title}</h2>
        <p className="text-2xl font-bold text-gray-800">{value}</p>
        <p className={`text-sm mt-1 flex items-center ${isPositive ? "text-green-500" : "text-red-500"}`}>
          {isPositive ? <FaArrowUp className="mr-1" /> : <FaArrowDown className="mr-1" />}
          {Math.abs(change)}% Since last week
        </p>
      </div>
      <div className={`bg-${color}-500 text-white p-3 rounded-full text-xl`}>{icon}</div>
    </div>
  );
};

export default CardStat;