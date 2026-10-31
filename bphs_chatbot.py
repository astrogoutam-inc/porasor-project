"""BPHS-grounded AI response service. API keys are read only from server env."""
import os, re, json, urllib.request, urllib.error
from typing import Dict, Any, List, Optional
from bphs_reader import BPHSDataReader
from bphs_book_retriever import BPHSBookRetriever

class BPHSChatbotEngine:
    def __init__(self, reader_instance: BPHSDataReader):
        self.reader=reader_instance
        self.book=BPHSBookRetriever()
        self.api_key=os.getenv("OPENAI_API_KEY","").strip()
        self.model=os.getenv("OPENAI_MODEL","gpt-4.1-mini")
        self.base_url=os.getenv("OPENAI_BASE_URL","https://api.openai.com/v1/chat/completions")

    def _context(self, data:Dict[str,Any])->str:
        calc=data.get("horoscope_calculations",{})
        selected={k:calc.get(k) for k in ["ascendant_longitude","ascendant_sign","planets","shodashvarga","yogas","dasha_at_birth","current_dasha","current_transit_analysis","vimsopaka_scores","precision_engine"] if k in calc}
        # Send only the running Mahadasha and the next Mahadasha to the LLM;
        # the full 120-year nested timeline remains available in the API response.
        timeline=calc.get("vimshottari_timeline") or {}
        periods=timeline.get("timeline",[])
        current=timeline.get("current",{})
        current_start=current.get("start_utc")
        start_index=next((i for i,x in enumerate(periods) if x.get("start_utc")==current_start),0)
        selected["vimshottari_timing_context"]={"system":timeline.get("system"),"nakshatra":timeline.get("nakshatra"),"current":current,"current_and_next_mahadashas":periods[start_index:start_index+2]}
        selected["user_info"]=data.get("user_info",{})
        selected["bphs_predictions"]=data.get("bphs_predictions",{})
        selected["current_transit"]=data.get("current_transit",{})
        return json.dumps(selected,ensure_ascii=False,default=str)

    def build_system_prompt(self)->str:
        return """আপনি একজন উন্নত Parashari Vedic Astrology research assistant। ব্যবহারকারীর ভাষা অনুসরণ করুন; বাংলা প্রশ্নে প্রাঞ্জল বাংলায় উত্তর দিন। প্রশ্নের বিষয় অনুযায়ী প্রাসঙ্গিক ভাব, ভাবপতি, গ্রহ, যোগ, D1/D9/D10 (যদি ডেটা থাকে), Vimshottari মহাদশা-অন্তর্দশা-প্রত্যন্তরদশা এবং প্রদত্ত বর্তমান গোচর-জন্মকুণ্ডলী সংযোগ বিচার করুন।

প্রতিটি উত্তরে প্রথমে সরাসরি উত্তর, পরে কুণ্ডলীর নির্দিষ্ট প্রমাণ, দশা, গোচর, সহায়ক ও বিরোধী ইঙ্গিত এবং সময়সীমা দিন। সময় জানতে চাইলে কেবল প্রদত্ত প্রকৃত timeline থেকে তারিখ/সময় নিন; তথ্য না থাকলে স্পষ্টভাবে বলুন। কোনো গ্রহ, দশা, যোগ, শ্লোক, ভবিষ্যৎ ঘটনা বা BPHS সূত্র বানাবেন না। Database-এ fallback/অনিশ্চিত তথ্য থাকলে সেটিকে শাস্ত্রীয় নিশ্চিত সূত্র বলে উপস্থাপন করবেন না। Retrieved মূল বইয়ের page-context-এ যে page number দেওয়া আছে, কেবল সেই পৃষ্ঠাই cite করতে পারবেন; retrieval না থাকলে কোনো page/shloka reference বানাবেন না।

অর্থ: 2,5,9,10,11 ভাব এবং সংশ্লিষ্ট অধিপতি/ধনযোগ; কর্ম: 2,6,10,11; বিবাহ: 7ম ভাব, 7মপতি, শুক্র, D9; সন্তান: 5ম ভাব, বৃহস্পতি, D7; সম্পত্তি: 4র্থ ভাব, মঙ্গল; বিদেশ: 9ম/12শ/7ম; স্বাস্থ্য: 1ম/6ষ্ঠ/8ম/12শ ও সংশ্লিষ্ট দশা। এগুলি প্রশ্নভিত্তিক সূচনা, যান্ত্রিক নিশ্চয়তা নয়।

মৃত্যুর নির্দিষ্ট দিন, তারিখ বা বয়স কখনো বলবেন না; আয়ু-সংক্রান্ত ঐতিহ্যগত বিচারকে অনিশ্চিত বলে ব্যাখ্যা করুন এবং ভয় সৃষ্টি করবেন না। চিকিৎসা, আইন, বিনিয়োগ বা ঋণ সিদ্ধান্তে জ্যোতিষকে পেশাদার পরামর্শের বিকল্প বলবেন না।

উত্তর যথেষ্ট বিস্তারিত হবে, কিন্তু অপ্রাসঙ্গিক দীর্ঘতা নয়। আগের কথোপকথনের সঙ্গে ধারাবাহিকতা রাখুন এবং একই generic উত্তর পুনরাবৃত্তি করবেন না।"""


    @staticmethod
    def _sign_name(degree):
        signs = ["মেষ", "বৃষ", "মিথুন", "কর্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকর", "কুম্ভ", "মীন"]
        try: return signs[int(float(degree) // 30) % 12]
        except (TypeError, ValueError): return "তথ্য নেই"

    def generate_offline_response_payload(self, user_question: str, horoscope_data: Dict[str, Any], history=None) -> Dict[str, Any]:
        """Deterministic local response. No network call and no OpenAI API use."""
        calc = horoscope_data.get("horoscope_calculations") or {}
        planets = calc.get("planets") or {}
        if not planets or calc.get("ascendant_longitude") is None:
            raise RuntimeError("Offline বিশ্লেষণের জন্য আগে প্রকৃত জন্মকুণ্ডলী গণনা করুন।")
        q = user_question.lower()
        topic = "সাধারণ জন্মকুণ্ডলী"
        houses = [1, 9, 10, 11]
        if any(x in q for x in ["অর্থ", "টাকা", "আর্থিক", "ধন", "income", "finance", "money"]):
            topic, houses = "অর্থ ও আর্থিক সম্ভাবনা", [2, 5, 9, 10, 11]
        elif any(x in q for x in ["চাকরি", "ক্যারিয়ার", "কর্ম", "profession", "career", "job"]):
            topic, houses = "চাকরি ও কর্মজীবন", [2, 6, 10, 11]
        elif any(x in q for x in ["ব্যবসা", "business", "trade"]):
            topic, houses = "ব্যবসা", [2, 7, 10, 11]
        elif any(x in q for x in ["বিবাহ", "বিয়ে", "দাম্পত্য", "marriage"]):
            topic, houses = "বিবাহ ও সম্পর্ক", [2, 7, 8, 11]
        elif any(x in q for x in ["সন্তান", "child", "progeny"]):
            topic, houses = "সন্তান", [5, 9, 11]
        elif any(x in q for x in ["বিদেশ", "travel", "foreign"]):
            topic, houses = "বিদেশযাত্রা", [3, 7, 9, 12]
        elif any(x in q for x in ["বাড়ি", "বাড়ি", "জমি", "সম্পত্তি", "property"]):
            topic, houses = "বাড়ি ও সম্পত্তি", [4, 8, 11]
        elif any(x in q for x in ["স্বাস্থ্য", "রোগ", "health"]):
            topic, houses = "স্বাস্থ্যসংক্রান্ত জ্যোতিষীয় ইঙ্গিত", [1, 6, 8, 12]
        elif any(x in q for x in ["আয়ু", "মৃত্যু", "longevity", "death"]):
            topic, houses = "আয়ু-বিচারের ঐতিহ্যগত বিষয়", [1, 3, 8]
        elif any(x in q for x in ["দশা", "মহাদশা", "অন্তর্দশা", "dasha"]):
            topic, houses = "চলমান বিমশোত্তরী দশা", [1, 9, 10, 11]
        elif any(x in q for x in ["গোচর", "transit", "গ্রহের অবস্থান"]):
            topic, houses = "বর্তমান গোচর", [1, 9, 10, 11]

        asc_deg = float(calc.get("ascendant_longitude"))
        asc_sign = int(asc_deg // 30) % 12
        sign_names_en = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        sign_lords = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
        lines = [f"OFFLINE MODE — স্থানীয় গণনা ও সংরক্ষিত রেফারেন্স", f"প্রশ্নের বিষয়: {topic}", f"লগ্ন: {self._sign_name(asc_deg)} | লগ্নের ডিগ্রি: {asc_deg:.4f}°"]
        lines.append("\n১) জন্মকুণ্ডলীর প্রাসঙ্গিক গ্রহাবস্থান:")
        house_rows=[]
        for h in houses:
            sign_idx=(asc_sign+h-1)%12
            sign=sign_names_en[sign_idx]
            lord=sign_lords[sign]
            lord_deg=planets.get(lord)
            lord_house = (((int(float(lord_deg)//30)-asc_sign)%12)+1) if lord_deg is not None else None
            occupying=[f"{pl} ({self._sign_name(deg)})" for pl,deg in planets.items() if ((int(float(deg)//30)-asc_sign)%12)+1==h]
            row=f"{h}ম ভাব: {self._sign_name(sign_idx*30)} রাশি; অধিপতি {lord}"
            row += f", অধিপতি অবস্থান {lord_house}ম ভাবে" if lord_house else ", অধিপতির অবস্থান ডেটা নেই"
            row += "; অবস্থানকারী গ্রহ: "+(", ".join(occupying) if occupying else "কোনো গ্রহ নেই")
            lines.append(row); house_rows.append({"house":h,"sign":sign,"lord":lord,"lord_house":lord_house,"occupants":occupying})

        current=calc.get("current_dasha") or (calc.get("vimshottari_timeline") or {}).get("current") or {}
        lines.append("\n২) বর্তমান বিমশোত্তরী দশা:")
        if current:
            lines.append("মহাদশা: {0} | অন্তর্দশা: {1} | প্রত্যন্তরদশা: {2}".format(current.get("mahadasha","তথ্য নেই"),current.get("antardasha","তথ্য নেই"),current.get("pratyantardasha","তথ্য নেই")))
            lines.append("সময়: {0} থেকে {1}".format(current.get("start_utc","অপ্রদত্ত"),current.get("end_utc","অপ্রদত্ত")))
        else: lines.append("চলমান দশার নির্ভরযোগ্য তথ্য এই চার্ট ডেটায় নেই।")

        trans=(calc.get("current_transit_analysis") or horoscope_data.get("current_transit") or {})
        lines.append("\n৩) বর্তমান গোচর-জন্মকুণ্ডলী সংযোগ:")
        transit_houses=trans.get("transiting_planets_in_natal_whole_sign_houses",[])
        aspects=trans.get("parashari_transit_to_natal_planet_aspects",[])
        if transit_houses:
            for item in transit_houses[:12]: lines.append(json.dumps(item,ensure_ascii=False,default=str))
        else: lines.append("গোচর-ভাবে গ্রহের অবস্থানের বিস্তারিত তালিকা পাওয়া যায়নি।")
        if aspects:
            lines.append(f"পরাশরী দৃষ্টি-সংযোগের নথিভুক্ত সংখ্যা: {len(aspects)}")
            for item in aspects[:10]: lines.append(json.dumps(item,ensure_ascii=False,default=str))
        else: lines.append("দৃষ্টি-সংযোগের তথ্য অনুপস্থিত।")

        yogas=calc.get("yogas") or []
        lines.append("\n৪) গণনায় শনাক্ত যোগ:")
        lines.extend([str(y) for y in yogas[:15]] if yogas else ["এই গণনার ফলাফলে শনাক্ত যোগের তালিকা নেই।"])

        preds=horoscope_data.get("bphs_predictions") or {}
        bhava_preds=preds.get("bhava_predictions") or []
        selected=[x for x in bhava_preds if x.get("lord_house") in houses]
        if selected:
            lines.append("\n৫) স্থানীয় BPHS ডেটাবেসে পাওয়া সংশ্লিষ্ট ভাবাধিপতির রেফারেন্স:")
            for x in selected:
                text=x.get("description_bn") or x.get("prediction_bn") or ""
                status=x.get("source_status","database")
                lines.append(f"{x.get('title_bn','')} — {text} [ডেটা-স্ট্যাটাস: {status}]")

        retrieved=self.book.search(user_question,limit=3)
        if retrieved:
            lines.append("\n৬) স্থানীয় BPHS বই থেকে অনুসন্ধান-ফল (এটি উদ্ধৃত অংশ, AI-ব্যাখ্যা নয়):")
            for item in retrieved:
                excerpt=re.sub(r"\s+"," ",item.get("excerpt","")).strip()
                lines.append(f"পৃষ্ঠা {item['page']}: {excerpt[:650]}")

        lines.append("\nসীমাবদ্ধতা: OFFLINE MODE-এ কোনো জেনারেটিভ AI বা ইন্টারনেট ব্যবহার করা হয়নি। উপরের তথ্য স্থানীয় ক্যালকুলেশন/ডেটাবেস/বইয়ের অনুসন্ধান-ফল; এটি পূর্ণাঙ্গ মানবীয় শাস্ত্রীয় বিচার বা নিশ্চিত ভবিষ্যদ্বাণী নয়। যে তথ্য অনুপস্থিত, তা অনুমান করা হয়নি। মৃত্যুর নির্দিষ্ট তারিখ বা বয়স নির্ধারণ করা হয় না; স্বাস্থ্য/অর্থ/আইন বিষয়ে পেশাদার পরামর্শের বিকল্প নয়।")
        return {"status":"success","mode":"offline","user_question":user_question,"bot_response":"\n".join(lines),"grounding_sources_used":["local horoscope calculation","local BPHS database","local BPHS book search" if retrieved else "local horoscope calculation"],"book_pages_retrieved":[x["page"] for x in retrieved]}

    def generate_bot_response_payload(self,user_question:str,horoscope_data:Dict[str,Any],history:Optional[List[Dict[str,str]]]=None)->Dict[str,Any]:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY backend environment variable is not configured.")
        retrieved=self.book.search(user_question,limit=5)
        book_context=json.dumps(retrieved,ensure_ascii=False)
        messages=[{"role":"system","content":self.build_system_prompt()},
                  {"role":"system","content":"নিচের কুণ্ডলী ও গণনার ডেটাই একমাত্র ব্যক্তিগত গণনা-উৎস। অনুপস্থিত মান অনুমান করবেন না।\n"+self._context(horoscope_data)},
                  {"role":"system","content":"প্রাসঙ্গিক মূল BPHS বইয়ের page-retrieval ফল (শুধু এগুলিতে থাকা page number উদ্ধৃত করুন; ফল না থাকলে বইয়ের পৃষ্ঠা দাবি করবেন না):\n"+book_context}]
        for item in (history or [])[-16:]:
            role=item.get("role"); content=item.get("content","")
            if role in ("user","assistant") and isinstance(content,str) and content.strip():
                messages.append({"role":role,"content":content[:12000]})
        messages.append({"role":"user","content":user_question})
        body=json.dumps({"model":self.model,"messages":messages,"temperature":0.45,"max_tokens":3000}).encode()
        req=urllib.request.Request(self.base_url,data=body,headers={"Authorization":"Bearer "+self.api_key,"Content-Type":"application/json"},method="POST")
        try:
            with urllib.request.urlopen(req,timeout=90) as res: result=json.loads(res.read().decode())
            answer=result["choices"][0]["message"]["content"].strip()
            if not answer: raise RuntimeError("AI returned an empty answer")
            return {"status":"success","mode":"online","user_question":user_question,"bot_response":answer,"model":self.model,"grounding_sources_used":["bphs_database_schema.json","computed horoscope data"],"book_pages_retrieved":[x["page"] for x in retrieved]}
        except urllib.error.HTTPError as e:
            detail=e.read().decode("utf-8",errors="replace")
            raise RuntimeError(f"OpenAI API HTTP {e.code}: {detail[:1200]}")
