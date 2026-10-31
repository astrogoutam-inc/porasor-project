import React from 'react';

/**
 * North Indian Diamond Style Kundali Chart Component (SVG)
 * Renders Houses 1 to 12 in the traditional diamond format.
 */
const KundaliChart = ({ ascendantSign = 8, housePlanets = {} }) => {
  const getHouseSign = (houseNum) => {
    let sign = (ascendantSign + houseNum - 1) % 12;
    return sign === 0 ? 12 : sign;
  };

  const houseCenters = {
    1: { x: 200, y: 100 },
    2: { x: 100, y: 50 },
    3: { x: 50, y: 100 },
    4: { x: 100, y: 200 },
    5: { x: 50, y: 300 },
    6: { x: 100, y: 350 },
    7: { x: 200, y: 300 },
    8: { x: 300, y: 350 },
    9: { x: 350, y: 300 },
    10: { x: 300, y: 200 },
    11: { x: 350, y: 100 },
    12: { x: 300, y: 50 }
  };

  return (
    <div style={{ width: '100%', maxWidth: '500px', margin: '0 auto', textAlign: 'center' }}>
      <h3 style={{ fontFamily: 'sans-serif', color: '#4A154B' }}>लग्न কুণ্ডলী (D1 Rasi Chart)</h3>
      
      <svg viewBox="0 0 400 400" style={{ border: '2px solid #8B0000', backgroundColor: '#FFFDF5', borderRadius: '8px' }}>
        <rect x="10" y="10" width="380" height="380" fill="none" stroke="#8B0000" strokeWidth="2" />
        <line x1="10" y1="10" x2="390" y2="390" stroke="#8B0000" strokeWidth="1.5" />
        <line x1="390" y1="10" x2="10" y2="390" stroke="#8B0000" strokeWidth="1.5" />
        <polygon points="200,10 390,200 200,390 10,200" fill="none" stroke="#8B0000" strokeWidth="1.5" />

        {Object.keys(houseCenters).map((houseStr) => {
          const houseNum = parseInt(houseStr);
          const center = houseCenters[houseNum];
          const signNum = getHouseSign(houseNum);
          const planets = housePlanets[houseNum] || [];

          return (
            <g key={houseNum}>
              <text
                x={center.x}
                y={center.y - 15}
                fontSize="12"
                fontWeight="bold"
                fill="#B22222"
                textAnchor="middle"
              >
                {signNum}
              </text>
              <text
                x={center.x}
                y={center.y + 10}
                fontSize="13"
                fontWeight="600"
                fill="#000000"
                textAnchor="middle"
              >
                {planets.join(', ')}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

export default KundaliChart;
