import React, { useEffect, useRef, useState } from 'react';

const ChatbotWidget = ({ horoscopeData, apiBaseUrl = '' }) => {
  const [mode, setMode] = useState('online');
  const [onlineConfigured, setOnlineConfigured] = useState(null);
  const [messages, setMessages] = useState([{sender:'bot', text:'নমস্কার। Online Mode-এ AI-ভিত্তিক বিশ্লেষণ এবং Offline Mode-এ স্থানীয় গণনা ও BPHS রেফারেন্স ব্যবহার করতে পারবেন। প্রথমে জন্মকুণ্ডলী গণনা করুন।'}]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);
  useEffect(() => { endRef.current?.scrollIntoView({behavior:'smooth'}); }, [messages, loading]);
  useEffect(() => { fetch(`${apiBaseUrl}/api/chatbot-status`).then(r=>r.json()).then(d=>setOnlineConfigured(!!d.online_configured)).catch(()=>setOnlineConfigured(false)); }, [apiBaseUrl]);
  const quickQuestions = ['আমার অর্থভাগ্য কবে উন্নতি হতে পারে?','চলমান মহাদশা ও অন্তর্দশার ফল ব্যাখ্যা করুন','চাকরি ও কর্মজীবনের সম্ভাবনা বিচার করুন','বর্তমান গোচর জন্মকুণ্ডলীর কোন গ্রহকে প্রভাবিত করছে?'];
  const handleSend = async (query) => {
    const question = (query ?? inputQuery).trim();
    if (!question || loading) return;
    if (!horoscopeData?.horoscope_calculations?.planets) {
      setMessages(prev => [...prev,{sender:'bot',text:'প্রথমে জন্মতারিখ, জন্মসময় ও জন্মস্থান দিয়ে প্রকৃত জন্মকুণ্ডলী গণনা সম্পন্ন করুন।'}]); return;
    }
    if (mode === 'online' && onlineConfigured === false) {
      setMessages(prev => [...prev,{sender:'bot',text:'Online AI বর্তমানে সংযুক্ত নয়। Backend-এ OPENAI_API_KEY সেট করুন, অথবা উপরের সুইচ থেকে Offline Mode নির্বাচন করুন।'}]); return;
    }
    const history = messages.slice(-16).map(m => ({role:m.sender==='user'?'user':'assistant',content:m.text}));
    setMessages(prev => [...prev,{sender:'user',text:question}]); setInputQuery(''); setLoading(true);
    try {
      const res = await fetch(`${apiBaseUrl}/api/chatbot-query`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_question:question,horoscope_data:horoscopeData,conversation_history:history,mode})});
      const data = await res.json(); if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
      if (!data.bot_response) throw new Error('খালি উত্তর পাওয়া গেছে।');
      setMessages(prev => [...prev,{sender:'bot',text:data.bot_response,mode:data.mode}]);
    } catch (e) { setMessages(prev => [...prev,{sender:'bot',text:`${mode==='online'?'Online AI':'Offline Engine'}-এ সমস্যা: ${e.message}`}]); }
    finally { setLoading(false); }
  };
  const switchMode = (next) => { if (loading) return; setMode(next); setMessages(prev=>[...prev,{sender:'bot',text:next==='online'?'ONLINE MODE চালু হয়েছে। উত্তর তৈরিতে Backend AI ব্যবহার হবে।':'OFFLINE MODE চালু হয়েছে। কোনো OpenAI API বা ইন্টারনেট কল হবে না; শুধু স্থানীয় গণনা ও সংরক্ষিত রেফারেন্স ব্যবহার হবে।'}]); };
  return <section style={{background:'#fff',border:'1px solid #e2e8f0',borderRadius:18,boxShadow:'0 12px 32px rgba(15,23,42,.10)',maxWidth:960,margin:'20px auto',overflow:'hidden',color:'#172033'}}>
    <header style={{background:'linear-gradient(120deg,#10213d,#243f69)',color:'#fff',padding:'20px 22px'}}><h2 style={{margin:0,fontSize:21}}>ASTROLOGER GOUOTAM — AI Astrology Assistant</h2><p style={{margin:'6px 0 0',opacity:.85,fontSize:13}}>BPHS • D1 / D9 • Vimshottari Dasha • Transit-to-Natal</p></header>
    <div style={{padding:'14px 18px',background:'#f8fafc',borderBottom:'1px solid #e5eaf1'}}>
      <div style={{fontSize:12,fontWeight:800,letterSpacing:'.08em',color:'#64748b',marginBottom:9}}>SELECT CHATBOT MODE</div>
      <div role="group" aria-label="Chatbot mode" style={{display:'flex',gap:8,flexWrap:'wrap'}}>
        <button onClick={()=>switchMode('online')} aria-pressed={mode==='online'} style={{flex:1,minWidth:130,padding:'11px 14px',borderRadius:12,border:mode==='online'?'2px solid #16845b':'1px solid #cbd5e1',background:mode==='online'?'#e8f7ef':'#fff',color:'#14543b',fontWeight:800,cursor:'pointer'}}>● ONLINE MODE</button>
        <button onClick={()=>switchMode('offline')} aria-pressed={mode==='offline'} style={{flex:1,minWidth:130,padding:'11px 14px',borderRadius:12,border:mode==='offline'?'2px solid #2563eb':'1px solid #cbd5e1',background:mode==='offline'?'#eaf2ff':'#fff',color:'#1e40af',fontWeight:800,cursor:'pointer'}}>● OFFLINE MODE</button>
      </div>
      <div style={{fontSize:12,color:'#475569',marginTop:9,lineHeight:1.55}}>{mode==='online'?'AI-ভিত্তিক বিস্তারিত উত্তর। ইন্টারনেট, Backend এবং API Key প্রয়োজন।': 'ইন্টারনেট/API প্রয়োজন নেই। স্থানীয় জন্মকুণ্ডলী, দশা, গোচর ডেটা ও BPHS রেফারেন্স থেকে সীমাবদ্ধ কিন্তু যাচাইযোগ্য উত্তর।'} {onlineConfigured===false && mode==='online' ? <b style={{color:'#b45309'}}> Online API Key পাওয়া যায়নি।</b> : null}</div>
    </div>
    <div style={{display:'flex',gap:8,padding:12,overflowX:'auto',background:'#fff'}}>{quickQuestions.map(q=><button key={q} disabled={loading} onClick={()=>handleSend(q)} style={{whiteSpace:'nowrap',border:'1px solid #cbd5e1',borderRadius:18,padding:'8px 12px',background:'#f8fafc',cursor:'pointer',fontSize:12}}>{q}</button>)}</div>
    <div style={{height:440,maxHeight:'58vh',minHeight:280,overflowY:'auto',padding:16,background:'#f5f7fb'}}>{messages.map((m,i)=><div key={i} style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere',lineHeight:1.75,maxWidth:'94%',margin:'10px 0 10px '+(m.sender==='user'?'auto':'0'),padding:14,borderRadius:14,background:m.sender==='user'?'#e1edff':'#fff',border:'1px solid #e2e8f0',boxShadow:'0 2px 6px rgba(15,23,42,.04)'}}>{m.sender==='bot'&&m.mode&&<div style={{fontSize:10,fontWeight:800,color:m.mode==='offline'?'#1d4ed8':'#047857',marginBottom:5}}>{m.mode.toUpperCase()} RESPONSE</div>}{m.text}</div>)}{loading&&<div style={{padding:12,color:'#475569'}}> {mode==='online'?'AI আপনার প্রশ্ন ও কুণ্ডলী বিশ্লেষণ করছে…':'স্থানীয় জ্যোতিষ ডেটা সাজানো হচ্ছে…'}</div>}<div ref={endRef}/></div>
    <form onSubmit={e=>{e.preventDefault();handleSend();}} style={{display:'flex',gap:9,padding:14,borderTop:'1px solid #e5eaf1',background:'#fff'}}><input value={inputQuery} onChange={e=>setInputQuery(e.target.value)} placeholder="আপনার প্রশ্ন লিখুন…" aria-label="আপনার প্রশ্ন" style={{flex:1,minWidth:0,padding:'13px 15px',border:'1px solid #cbd5e1',borderRadius:24,fontSize:14}}/><button disabled={loading} style={{padding:'0 22px',border:0,borderRadius:24,background:'#17345c',color:'#fff',fontWeight:700,cursor:'pointer'}}>পাঠান</button></form>
  </section>;
};
export default ChatbotWidget;
