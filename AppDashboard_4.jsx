import React, { useState } from 'react';
import DualKundaliView from './DualKundaliView';
import ChatbotWidget from './ChatbotWidget';

/**
 * Main Application Dashboard (React)
 * Complete Vedic Astrology Software Suite according to Brihat Parasara Hora Sastra.
 */
const AppDashboard = () => {
  const [formData, setFormData] = useState({
    name: '',
    dob: '',
    tob: '',
    place: 'Kolkata, India',
    lat: 22.5726,
    lon: 88.3639,
    timezone_offset: 5.5
  });

  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('D1');

  const [horoscopeData, setHoroscopeData] = useState(null);
  const [apiError, setApiError] = useState('');

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleCalculate = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('/api/calculate-horoscope', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.name,
          date_of_birth: formData.dob,
          time_of_birth: formData.tob,
          latitude: parseFloat(formData.lat),
          longitude: parseFloat(formData.lon),
          timezone_offset: parseFloat(formData.timezone_offset)
        })
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || `HTTP ${response.status}`);
      setHoroscopeData(result);
      setApiError('');
      setLoading(false);
    } catch (err) {
      setApiError(err.message || 'Backend connection failed');
      setLoading(false);
    }
  };

  // Dynamic Data Extraction
  const calc = horoscopeData?.horoscope_calculations || {};
  const dasha = calc.dasha_at_birth || {};
  const RASI_NAMES = ["মেষ", "বৃষ", "মিথুন", "কর্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকর", "কুম্ভ", "মীন"];

  const ascSignName = calc.ascendant_sign ? `${RASI_NAMES[calc.ascendant_sign - 1]} (Sign #${calc.ascendant_sign})` : 'গণনার অপেক্ষায়';
  const moonDeg = calc.planets?.Moon ?? 0;
  const moonSignName = calc.planets?.Moon != null ? `${RASI_NAMES[Math.floor(moonDeg / 30)]} (Sign #${Math.floor(moonDeg / 30) + 1})` : 'গণনার অপেক্ষায়';

  // Helper function to map calculated planetary longitudes to house numbers (1-12)
  const getHousePlanets = () => {
    const ascendantSignNum = calc.ascendant_sign || 1;
    const hp = { 1: ["Asc"], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: [] };

    if (calc.planets) {
      Object.entries(calc.planets).forEach(([p, deg]) => {
        const pSign = Math.floor(deg / 30) + 1;
        const house = (((pSign - ascendantSignNum) % 12) + 12) % 12 + 1;
        const codeMap = {
          Sun: 'Su', Moon: 'Mo', Mars: 'Ma', Mercury: 'Me',
          Jupiter: 'Ju', Venus: 'Ve', Saturn: 'Sa', Rahu: 'Ra', Ketu: 'Ke'
        };
        const code = codeMap[p] || p.slice(0, 2);
        hp[house].push(code);
      });
    }
    return hp;
  };

  return (
    <div style={{ backgroundColor: '#F4F6F7', minHeight: '100vh', padding: '24px', fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif" }}>
      
      {/* App Header */}
      <header style={{ textAlign: 'center', marginBottom: '28px', background: 'linear-gradient(135deg, #8B0000 0%, #4A154B 100%)', padding: '24px', borderRadius: '16px', color: '#FFFFFF', boxShadow: '0 6px 18px rgba(0,0,0,0.12)' }}>
        <h1 style={{ margin: 0, fontSize: '2.2rem', fontFamily: 'Georgia, serif' }}>বৃহৎ পরাশর হোরা শাস্ত্র (BPHS) বৈদিক অ্যাস্ট্রোলজি অ্যাপ</h1>
        <p style={{ margin: '8px 0 0 0', opacity: 0.9, fontSize: '1.05rem' }}>
          নিখুঁত ষোড়শবর্গ কুণ্ডলী, লাইভ গোচর কুণ্ডলী এবং BPHS-ভিত্তিক AI চ্যাটবট সিস্টেম
        </p>
      </header>

      {/* 1. User Input Section */}
      <section style={{ background: '#FFFFFF', padding: '20px 24px', borderRadius: '16px', boxShadow: '0 4px 14px rgba(0,0,0,0.06)', marginBottom: '28px' }}>
        <h3 style={{ margin: '0 0 16px 0', color: '#2C3E50', borderBottom: '2px solid #EAECEE', paddingBottom: '8px' }}>
          📝 জন্ম বিবরণ ইনপুট সেকশন (User Birth Details Input)
        </h3>
        
        <form onSubmit={handleCalculate} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', alignItems: 'end' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 'bold', color: '#566573', marginBottom: '6px' }}>নাম (Name)</label>
            <input type="text" name="name" value={formData.name} onChange={handleInputChange} required style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #D5D8DC' }} />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 'bold', color: '#566573', marginBottom: '6px' }}>জন্ম তারিখ (DOB)</label>
            <input type="date" name="dob" value={formData.dob} onChange={handleInputChange} required style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #D5D8DC' }} />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 'bold', color: '#566573', marginBottom: '6px' }}>জন্ম সময় (TOB)</label>
            <input type="time" step="1" name="tob" value={formData.tob} onChange={handleInputChange} required style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #D5D8DC' }} />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 'bold', color: '#566573', marginBottom: '6px' }}>জন্মস্থান (Place of Birth)</label>
            <input type="text" name="place" value={formData.place} onChange={handleInputChange} required style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #D5D8DC' }} />
          </div>

          <div>
            <label style={{display:'block',fontWeight:600,marginBottom:6}}>টাইমজোন UTC Offset</label>
            <input name="timezone_offset" type="number" step="0.25" value={formData.timezone_offset} onChange={handleInputChange} style={{width:'100%',padding:10,border:'1px solid #ccc',borderRadius:8}} />
          </div>
          <button type="submit" disabled={loading} style={{ background: '#8B0000', color: '#FFFFFF', padding: '12px 20px', border: 'none', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer', height: '42px' }}>
            {loading ? 'গণনা করা হচ্ছে...' : 'কুণ্ডলী ও ফলাফল বের করুন'}
          </button>
        </form>
      </section>

      {/* 2. Top Astrological Dynamic Summary Cards */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '28px' }}>
        <div style={{ background: '#FFFFFF', padding: '16px', borderRadius: '12px', borderLeft: '4px solid #8B0000', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
          <span style={{ fontSize: '0.8rem', color: '#7F8C8D', fontWeight: 'bold' }}>লগ্ন (Lagna)</span>
          <h3 style={{ margin: '4px 0 0 0', color: '#2C3E50' }}>{ascSignName}</h3>
        </div>

        <div style={{ background: '#FFFFFF', padding: '16px', borderRadius: '12px', borderLeft: '4px solid #2980B9', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
          <span style={{ fontSize: '0.8rem', color: '#7F8C8D', fontWeight: 'bold' }}>রাশি (Moon Sign)</span>
          <h3 style={{ margin: '4px 0 0 0', color: '#2C3E50' }}>{moonSignName}</h3>
        </div>

        <div style={{ background: '#FFFFFF', padding: '16px', borderRadius: '12px', borderLeft: '4px solid #27AE60', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
          <span style={{ fontSize: '0.8rem', color: '#7F8C8D', fontWeight: 'bold' }}>নক্ষত্র (Nakshatra)</span>
          <h3 style={{ margin: '4px 0 0 0', color: '#2C3E50' }}>{dasha.moon_nakshatra || 'গণনার অপেক্ষায়'}</h3>
        </div>

        <div style={{ background: '#FFFFFF', padding: '16px', borderRadius: '12px', borderLeft: '4px solid #8E44AD', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
          <span style={{ fontSize: '0.8rem', color: '#7F8C8D', fontWeight: 'bold' }}>বর্তমান মহাদশা (Dasha)</span>
          <h3 style={{ margin: '4px 0 0 0', color: '#2C3E50' }}>{calc.current_dasha?.mahadasha ? `${calc.current_dasha.mahadasha} / ${calc.current_dasha.antardasha || '—'}` : 'গণনার অপেক্ষায়'}</h3>
        </div>

        <div style={{ background: '#FFFFFF', padding: '16px', borderRadius: '12px', borderLeft: '4px solid #D35400', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
          <span style={{ fontSize: '0.8rem', color: '#7F8C8D', fontWeight: 'bold' }}>শুভ মুহূর্ত (Panchang)</span>
          <h3 style={{ margin: '4px 0 0 0', color: '#2C3E50' }}>পঞ্জিকা গণনা এই সংস্করণে সংযুক্ত নয়</h3>
        </div>
      </section>

      {/* 3. Shodashvarga Chart Selector Tabs */}
      <section style={{ background: '#FFFFFF', padding: '16px', borderRadius: '16px', marginBottom: '28px', boxShadow: '0 4px 14px rgba(0,0,0,0.06)' }}>
        <h4 style={{ margin: '0 0 12px 0', color: '#2C3E50' }}>ষোড়শবর্গ চার্ট নির্বাচন করুন (16 Divisional Charts)</h4>
        <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '8px' }}>
          {['D1 Rasi', 'D2 Hora', 'D3 Drekkana', 'D7 Saptamamsa', 'D9 Navamsa', 'D10 Dasamsa', 'D12 Dwadasamsa', 'D60 Shashtiamsa'].map((chart) => (
            <button
              key={chart}
              onClick={() => setActiveTab(chart.split(' ')[0])}
              style={{
                padding: '8px 16px',
                borderRadius: '20px',
                border: '1px solid #D5D8DC',
                background: activeTab === chart.split(' ')[0] ? '#8B0000' : '#FFFFFF',
                color: activeTab === chart.split(' ')[0] ? '#FFFFFF' : '#2C3E50',
                cursor: 'pointer',
                fontWeight: 'bold',
                fontSize: '0.85rem'
              }}
            >
              {chart}
            </button>
          ))}
        </div>
      </section>

      {apiError && <div role="alert" style={{background:'#fee2e2',color:'#991b1b',padding:12,borderRadius:8,marginBottom:16}}>{apiError}</div>}
      {/* Render only actual calculated data; never show sample/demo chart values. */}
      {horoscopeData && <section style={{ marginBottom: '32px' }}>
        <DualKundaliView birthChart={{ascendantSign:calc.ascendant_sign,housePlanets:getHousePlanets(),date:formData.dob,shodashvarga:calc.shodashvarga,planets:calc.planets}} transitData={calc.current_transit_analysis} />
      </section>}

      {/* 5. BPHS AI Chatbot Widget */}
      <section>
        <ChatbotWidget horoscopeData={horoscopeData} />
      </section>

    </div>
  );
};

export default AppDashboard;
