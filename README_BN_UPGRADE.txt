BPHS ADVANCED CHATBOT + CALCULATION UPDATE
==========================================

এই আপডেটে যা বাস্তবে যোগ/সংশোধন করা হয়েছে
1) references/brihat_parashara_hora_shastra_english_v.pdf ও page-text: আপনার আগে দেওয়া সম্পূর্ণ BPHS ইংরেজি PDF এই ZIP-এ রাখা হয়েছে; bphs_book_retriever.py প্রশ্নের শব্দের সঙ্গে মেলা পৃষ্ঠা-চিহ্নিত অংশ AI-কে পাঠায়। এটি lexical retrieval, semantic vector search নয়।
2) bphs_chatbot.py: OpenAI Chat Completions API call, server-side API key, Bengali detailed system prompt, 16-message context history; fake fallback answer সরানো হয়েছে।
3) fastapi_app.py: জন্মসময়কে timezone_offset দিয়ে UTC-তে রূপান্তর; Swiss Ephemeris না থাকলে 503 error (নীরব approximate chart নয়); সম্পূর্ণ Vimshottari timeline ও বর্তমান MD/AD/PD; live transit-to-natal analysis।
4) bphs_timing.py: 120-year Vimshottari Mahadasha, nested Antardasha ও Pratyantardasha timeline; Parashari graha drishti contacts।
5) AppDashboard.jsx: fake sample birth chart সরানো, timezone offset input, actual API data-র উপর chart render।
6) DualKundaliView.jsx: D1, D9, live transit-to-natal view; fabricated example table বাদ।
7) ChatbotWidget.jsx: conversation history, real API error, no invented fallback prediction।

INSTALL / RUN
-------------
Python 3.10+ ব্যবহার করুন।
  pip install -r requirements.txt
  cp .env.example .env  (নিজের secret OPENAI_API_KEY server environment-এ দিন; .env GitHub-এ commit করবেন না)
  uvicorn fastapi_app:app --host 0.0.0.0 --port 8000

React frontend build/dev server-এ API proxy অথবা VITE_API_BASE_URL-সমতুল্য নির্দিষ্ট backend URL configure করতে হবে। ChatbotWidget/AppDashboard বর্তমানে same-origin '/api/...' ব্যবহার করে; cross-origin hosting হলে apiBaseUrl prop এবং CORS allow_origins-এ আপনার frontend domain বসান। Production-এ allow_origins=['*'] ব্যবহার করবেন না।

ACCURACY / IMPORTANT
---------------------
- Swiss Ephemeris + Lahiri ayanamsa code path বাধ্যতামূলক করা হয়েছে। Birth time is local civil time; timezone_offset অবশ্যই সঠিক দিতে হবে। DST প্রযোজ্য হলে ঐ জন্মস্থানের ঐ তারিখের প্রকৃত offset দিন।
- D1/D9 SVG chart values now come from calculated engine output; sample chart data was removed. D9 ascendant is computed from the same existing divisional formula.
- Existing engine's divisional chart formulae and yoga detection have NOT been independently certified against a professional ephemeris test suite. D9 rendering consumes the engine's existing D9 output; it is no longer a sample SVG, but the underlying D9 algorithm still requires independent test vectors.
- Transit-to-natal module calculates whole-sign house placement and classical Parashari 7th aspect for all planets, plus Mars 4/8, Jupiter 5/9, Saturn 3/10. It does not implement every advanced transit doctrine, retrograde station timing, combustion, Ashtakavarga, Shadbala transit weighting, Rahu/Ketu special aspect traditions, or event-certainty. Do not treat it as a finished prediction oracle.
- Vimshottari dates use 365.2425 days/year and nested proportional subperiods. Cross-check boundary dates against the exact year-length convention in the chosen classical reference/software before production use.
- Death date/age prediction is intentionally prohibited; no AI can reliably determine an individual's exact death date.
- The original tiny placeholder text file remains for compatibility. The complete previously uploaded BPHS English PDF and extracted page text are now included under references/. The page retriever is lexical and page-traceable but is not yet a human-audited scholarly index; always inspect cited page context for important interpretations.

DEPLOYMENT
----------
FastAPI is a separate Python service (Render config supplied). GitHub Pages cannot execute FastAPI/Python. Keep OPENAI_API_KEY only in backend environment secrets. Set frontend API base URL to deployed backend URL and restrict CORS to the frontend domain.

TEST
----
Run: python -m compileall .
Run basic module tests: python -c "from datetime import datetime; from bphs_timing import vimshottari_timeline; print(vimshottari_timeline(120,datetime(1990,1,1),datetime(2026,1,1))['current'])"


================ ONLINE / OFFLINE CHATBOT MODE ================

চ্যাটবটের উপরে ONLINE / OFFLINE দুটি কার্যকরী বাটন আছে।

ONLINE MODE:
- FastAPI Backend এবং OPENAI_API_KEY প্রয়োজন।
- OpenAI Chat Completions API-তে প্রশ্ন পাঠায়।
- স্থানীয় কুণ্ডলী, দশা, গোচর ও BPHS retrieval context পাঠানো হয়।

OFFLINE MODE:
- কোনো OpenAI API বা বাহ্যিক AI সার্ভারে প্রশ্ন পাঠায় না।
- স্থানীয় জন্মকুণ্ডলী, বর্তমান দশা, সংরক্ষিত গোচর বিশ্লেষণ, স্থানীয় BPHS database এবং bundled BPHS book text ব্যবহার করে deterministic summary দেয়।
- Offline উত্তর জেনারেটিভ AI-এর মতো মুক্ত বিশ্লেষণ নয়; ডেটা না থাকলে সেটি স্পষ্ট করে।

STATUS ENDPOINT: GET /api/chatbot-status
CHAT ENDPOINT: POST /api/chatbot-query (mode: online অথবা offline)

গুরুত্বপূর্ণ: Offline mode-এও জন্মকুণ্ডলী গণনা আগে Backend-এর /api/calculate-horoscope দিয়ে করতে হবে। এই গণনার জন্য Swiss Ephemeris/PySwissEph ইনস্টল ও Backend চালু থাকা প্রয়োজন। অর্থাৎ Offline Mode বলতে AI API ছাড়া স্থানীয় chatbot analysis বোঝায়; এটি সম্পূর্ণ standalone mobile app নয়।
