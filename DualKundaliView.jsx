import React, { useState } from 'react';

/**
 * Single North Indian Diamond Style Kundali Chart Component
 */
export const SingleKundaliChart = ({ title, ascendantSign = 1, housePlanets = {}, chartColor = "#8B0000", bgColor = "#FFFDF5" }) => {
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
    <div style={{ flex: '1 1 350px', minWidth: '300px', maxWidth: '480px', margin: '10px auto', padding: '12px', background: '#FFFFFF', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }}>
      <h3 style={{ fontFamily: 'Georgia, serif', color: chartColor, marginTop: '0', marginBottom: '8px', textAlign: 'center', fontSize: '1.2rem' }}>
        {title}
      </h3>
      
      <svg viewBox="0 0 400 400" style={{ border: `2px solid ${chartColor}`, backgroundColor: bgColor, borderRadius: '8px', width: '100%', height: 'auto' }}>
        <rect x="10" y="10" width="380" height="380" fill="none" stroke={chartColor} strokeWidth="2" />
        <line x1="10" y1="10" x2="390" y2="390" stroke={chartColor} strokeWidth="1.5" />
        <line x1="390" y1="10" x2="10" y2="390" stroke={chartColor} strokeWidth="1.5" />
        <polygon points="200,10 390,200 200,390 10,200" fill="none" stroke={chartColor} strokeWidth="1.5" />

        {Object.keys(houseCenters).map((houseStr) => {
          const houseNum = parseInt(houseStr);
          const center = houseCenters[houseNum];
          const signNum = getHouseSign(houseNum);
          const planets = housePlanets[houseNum] || [];

          return (
            <g key={houseNum}>
              <text
                x={center.x}
                y={center.y - 12}
                fontSize="12"
                fontWeight="bold"
                fill={chartColor}
                textAnchor="middle"
              >
                {signNum}
              </text>
              <text
                x={center.x}
                y={center.y + 10}
                fontSize="13"
                fontWeight="600"
                fill="#1A1A1A"
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

/**
 * Dual View Component: Janma Kundali (Natal Chart) + Gochar Kundali (Live Transit Chart)
 */
const DualKundaliView = ({ 
  birthChart = { ascendantSign: 8, housePlanets: { 1: ["Asc", "Ma"], 2: ["Su"], 5: ["Ju"], 10: ["Mo"], 11: ["Ve"] }, date: "1995-10-15" },
  transitChart = { ascendantSign: 3, housePlanets: { 1: ["Asc"], 3: ["Su", "Me"], 5: ["Ju"], 8: ["Mo"], 10: ["Sa"], 11: ["Ra"] }, datetime: "2026-10-29 Live" }
}) => {
  const [activeTab, setActiveTab] = useState('both');

  return (
    <div style={{ fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif', maxWidth: '1050px', margin: '0 auto', padding: '16px' }}>
      
      {/* Header & Controls */}
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <h2 style={{ color: '#2C3E50', marginBottom: '6px' }}>বৈদিক কুণ্ডলী ডুয়াল-ভিউ (Dual Chart Dashboard)</h2>
        <p style={{ color: '#7F8C8D', fontSize: '0.95rem', margin: '0 0 16px 0' }}>
          জন্মকুণ্ডলী এবং বর্তমান মুহূর্তের লাইভ গোচর কুণ্ডলী পাশাপাশি বিশ্লেষণ করুন
        </p>

        {/* Responsive View Selector Tabs */}
        <div style={{ display: 'inline-flex', background: '#EAECEE', padding: '4px', borderRadius: '25px' }}>
          <button
            onClick={() => setActiveTab('natal')}
            style={{
              padding: '8px 18px',
              border: 'none',
              borderRadius: '20px',
              cursor: 'pointer',
              fontWeight: '600',
              backgroundColor: activeTab === 'natal' ? '#8B0000' : 'transparent',
              color: activeTab === 'natal' ? '#FFFFFF' : '#566573',
              transition: 'all 0.3s'
            }}
          >
            জন্মকুণ্ডলী (Natal)
          </button>
          <button
            onClick={() => setActiveTab('both')}
            style={{
              padding: '8px 18px',
              border: 'none',
              borderRadius: '20px',
              cursor: 'pointer',
              fontWeight: '600',
              backgroundColor: activeTab === 'both' ? '#2C3E50' : 'transparent',
              color: activeTab === 'both' ? '#FFFFFF' : '#566573',
              transition: 'all 0.3s'
            }}
          >
            পাশাপাশি (Dual View)
          </button>
          <button
            onClick={() => setActiveTab('transit')}
            style={{
              padding: '8px 18px',
              border: 'none',
              borderRadius: '20px',
              cursor: 'pointer',
              fontWeight: '600',
              backgroundColor: activeTab === 'transit' ? '#006699' : 'transparent',
              color: activeTab === 'transit' ? '#FFFFFF' : '#566573',
              transition: 'all 0.3s'
            }}
          >
            লাইভ গোচর (Transit)
          </button>
        </div>
      </div>

      {/* Side-by-Side Charts Container */}
      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '16px' }}>
        {(activeTab === 'both' || activeTab === 'natal') && (
          <SingleKundaliChart
            title={`জন্ম লগ্ন কুণ্ডলী (${birthChart.date || 'Janma'})`}
            ascendantSign={birthChart.ascendantSign}
            housePlanets={birthChart.housePlanets}
            chartColor="#8B0000"
            bgColor="#FFFDF5"
          />
        )}

        {(activeTab === 'both' || activeTab === 'transit') && (
          <SingleKundaliChart
            title={`আজকের লাইভ গোচর কুণ্ডলী (${transitChart.datetime || 'Live Transit'})`}
            ascendantSign={transitChart.ascendantSign}
            housePlanets={transitChart.housePlanets}
            chartColor="#006699"
            bgColor="#F0F8FF"
          />
        )}
      </div>

      {/* Summary Matrix / Comparative Table */}
      <div style={{ marginTop: '24px', background: '#FFFFFF', padding: '16px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }}>
        <h4 style={{ color: '#2C3E50', marginTop: 0, marginBottom: '12px', borderBottom: '2px solid #EAECEE', paddingBottom: '8px' }}>
          গ্রহের গোচর অবস্থান বিশ্লেষণ (Transit Position vs Natal)
        </h4>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
            <thead>
              <tr style={{ backgroundColor: '#F8F9F9', color: '#34495E' }}>
                <th style={{ padding: '10px', borderBottom: '2px solid #D5D8DC' }}>গ্রহ (Planet)</th>
                <th style={{ padding: '10px', borderBottom: '2px solid #D5D8DC' }}>জন্মকালীন ভাব (Natal House)</th>
                <th style={{ padding: '10px', borderBottom: '2px solid #D5D8DC' }}>বর্তমান গোচর ভাব (Live Transit)</th>
                <th style={{ padding: '10px', borderBottom: '2px solid #D5D8DC' }}>পরাশরী প্রভাব (Transit Effect)</th>
              </tr>
            </thead>
            <tbody>
              {[
                { planet: 'সূর্য (Sun)', natal: '২য় ভাব', transit: '৩য় ভাব', effect: 'শুভ (উদ্যম ও পরাক্রম বৃদ্ধি)' },
                { planet: 'চন্দ্র (Moon)', natal: '১০ম ভাব', transit: '৮ম ভাব', effect: 'মানসিক সতর্কতা প্রয়োজন' },
                { planet: 'মঙ্গল (Mars)', natal: '১ম ভাব (উচ্চস্থ)', transit: '৪র্থ ভাব', effect: 'স্থাবর সম্পত্তিতে মনোযোগ' },
                { planet: 'বৃহস্পতি (Jupiter)', natal: '৫ম ভাব', transit: '৫ম ভাব', effect: 'অত্যন্ত শুভ (জ্ঞান ও ভাগ্য বৃদ্ধি)' },
                { planet: 'শনি (Saturn)', natal: '৯ম ভাব', transit: '১০ম ভাব', effect: 'কর্মক্ষেত্রে দায়িত্ব বৃদ্ধি' },
              ].map((row, idx) => (
                <tr key={idx} style={{ backgroundColor: idx % 2 === 0 ? '#FFFFFF' : '#FBFCFC', borderBottom: '1px solid #EAECEE' }}>
                  <td style={{ padding: '10px', fontWeight: 'bold', color: '#2C3E50' }}>{row.planet}</td>
                  <td style={{ padding: '10px', color: '#8B0000' }}>{row.natal}</td>
                  <td style={{ padding: '10px', color: '#006699' }}>{row.transit}</td>
                  <td style={{ padding: '10px', color: '#27AE60', fontWeight: '500' }}>{row.effect}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};

export default DualKundaliView;
