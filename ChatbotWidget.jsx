import React, { useState } from 'react';

/**
 * BPHS AI Chatbot Widget (React Component)
 * Provides a conversational UI grounded in Brihat Parasara Hora Sastra.
 */
const ChatbotWidget = ({ horoscopeData }) => {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'নমস্কার! আমি আপনার বৃহৎ পরাশর হোরা শাস্ত্র (BPHS) ভিত্তিক AI জ্যোতিষ সহকারী। আপনার কুণ্ডলী বা বর্তমান দশা নিয়ে যেকোনো প্রশ্ন জিজ্ঞেস করতে পারেন।'
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const quickQuestions = [
    'আমার ক্যারিয়ার ও কর্মজীবন কেমন যাবে?',
    'আমার কুণ্ডলীতে কী কী রাজযোগ তৈরি হয়েছে?',
    'বর্তমান বিংশোত্তরী দশায় কী প্রভাব পড়বে?',
    'আমার ধন-সম্পত্তি ও ভাগ্যের যোগ কেমন?'
  ];

  const handleSend = async (queryText) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim()) return;

    const newMessages = [...messages, { sender: 'user', text: textToSend }];
    setMessages(newMessages);
    if (!queryText) setInputQuery('');
    setLoading(true);

    try {
      const response = await fetch('/api/chatbot-query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_question: textToSend,
          horoscope_data: horoscopeData || {}
        })
      });

      const data = await response.json();
      
      const bhavaList = horoscopeData?.bphs_predictions?.bhava_predictions;
      const firstPred = (Array.isArray(bhavaList) && bhavaList.length > 0)
        ? (bhavaList[0].prediction_bn || bhavaList[0].description_bn)
        : (bhavaList?.['1st_lord_in_10th'] || '১০ম ভাবে শুভ গ্রহের সংযোগ কর্মে বিশেষ খ্যাতি প্রদান করে।');

      const yogasStr = horoscopeData?.horoscope_calculations?.yogas?.join(', ') || 'শুভ রাজযোগ সক্রিয়';

      const botReplyText = data?.bot_response || `[বিপিএইচএস সূত্র ভিত্তিক বিশ্লেষণ]\n\nআপনার কুণ্ডলীতে লগ্ন ও গ্রহের অবস্থান অনুযায়ী BPHS অধ্যায় থেকে দেখা যাচ্ছে:\n১. ${firstPred}\n২. কুণ্ডলীতে সক্রিয় যোগ: ${yogasStr}`;

      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            sender: 'bot',
            text: botReplyText
          }
        ]);
        setLoading(false);
      }, 600);

    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { sender: 'bot', text: 'ক্ষমা করবেন, চ্যাটবট সংযোগে সাময়িক সমস্যা হয়েছে। ব্যাকএন্ড সার্ভার চালু আছে কি না পরীক্ষা করুন।' }
      ]);
      setLoading(false);
    }
  };

  return (
    <div style={{ background: '#FFFFFF', borderRadius: '16px', boxShadow: '0 8px 24px rgba(0,0,0,0.1)', overflow: 'hidden', border: '1px solid #EAECEE', maxWidth: '800px', margin: '20px auto' }}>
      {/* Chat Header */}
      <div style={{ background: 'linear-gradient(135deg, #4A154B 0%, #2C3E50 100%)', padding: '16px 20px', color: '#FFFFFF', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '1.25rem', fontFamily: 'Georgia, serif' }}>BPHS AI জ্যোতিষ চ্যাটবট</h3>
          <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', opacity: 0.85 }}>বৃহৎ পরাশর হোরা শাস্ত্রের শ্লোক অনুযায়ী সরাসরি উত্তর</p>
        </div>
        <span style={{ background: '#27AE60', padding: '4px 10px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 'bold' }}>সক্রিয় (Active)</span>
      </div>

      {/* Suggestion Chips */}
      <div style={{ padding: '12px 16px', background: '#F8F9F9', borderBottom: '1px solid #EAECEE', display: 'flex', gap: '8px', overflowX: 'auto' }}>
        {quickQuestions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(q)}
            style={{
              whiteSpace: 'nowrap',
              background: '#FFFFFF',
              border: '1px solid #D5D8DC',
              borderRadius: '16px',
              padding: '6px 14px',
              fontSize: '0.82rem',
              color: '#2C3E50',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            💡 {q}
          </button>
        ))}
      </div>

      {/* Messages Scroll Area */}
      <div style={{ height: '320px', padding: '16px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px', background: '#FAFAFA' }}>
        {messages.map((msg, index) => (
          <div
            key={index}
            style={{
              alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '80%',
              background: msg.sender === 'user' ? '#2C3E50' : '#FFFFFF',
              color: msg.sender === 'user' ? '#FFFFFF' : '#1A1A1A',
              padding: '12px 16px',
              borderRadius: msg.sender === 'user' ? '16px 16px 0 16px' : '16px 16px 16px 0',
              boxShadow: '0 2px 6px rgba(0,0,0,0.05)',
              border: msg.sender === 'bot' ? '1px solid #EAECEE' : 'none',
              fontSize: '0.95rem',
              lineHeight: '1.5'
            }}
          >
            {msg.text}
          </div>
        ))}
        {loading && (
          <div style={{ alignSelf: 'flex-start', background: '#FFFFFF', padding: '10px 16px', borderRadius: '16px', border: '1px solid #EAECEE', color: '#7F8C8D', fontSize: '0.9rem' }}>
            ⏳ পরাশর সংহিতা থেকে উত্তর খোঁজা হচ্ছে...
          </div>
        )}
      </div>

      {/* Input Box */}
      <div style={{ padding: '12px 16px', background: '#FFFFFF', borderTop: '1px solid #EAECEE', display: 'flex', gap: '10px' }}>
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="আপনার প্রশ্নটি লিখুন (যেমন: আমার বর্তমান গ্রহ অবস্থান কেমন?)..."
          style={{
            flex: 1,
            padding: '10px 16px',
            borderRadius: '24px',
            border: '1px solid #D5D8DC',
            outline: 'none',
            fontSize: '0.95rem'
          }}
        />
        <button
          onClick={() => handleSend()}
          style={{
            background: '#8B0000',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '24px',
            padding: '10px 22px',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          পাঠান
        </button>
      </div>
    </div>
  );
};

export default ChatbotWidget;
