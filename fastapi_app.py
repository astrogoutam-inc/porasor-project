"""
FastAPI Backend Application for BPHS Vedic Astrology Engine
Provides REST API endpoints for:
1. Birth Input & Horoscope Calculations (/api/calculate-horoscope)
2. Live Current Transit Chart (/api/live-transit-chart)
3. BPHS-Grounded AI Chatbot Query (/api/chatbot-query)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import datetime
from datetime import timezone, timedelta
from pathlib import Path
import os
import sys

# Dynamic Base Directory
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Import local BPHS modules
from bphs_engine import (
    ShodashvargaEngine, VimsopakaEngine, BPHSYogaEngine,
    VimshottariDashaEngine, BPHSSpecialJudgements, compute_astronomical_positions
)
from bphs_reader import BPHSDataReader
from bphs_chatbot import BPHSChatbotEngine
from bphs_timing import vimshottari_timeline, transit_to_natal

app = FastAPI(
    title="Brihat Parasara Hora Sastra (BPHS) Complete Astrology Suite",
    description="Full Vedic Astrology Backend with Shodashvarga, Live Transit, and BPHS-Grounded Chatbot.",
    version="4.0.0"
)

# Enable CORS for React/Vite Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in os.getenv("FRONTEND_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",") if x.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize BPHS Reader and Chatbot Engine
schema_paths = [
    str(BASE_DIR / "bphs_database_schema.json"),
    "/workspace/scratch/bphs_database_schema.json",
    "/workspace/artifacts/bphs_database_schema.json",
    "bphs_database_schema.json"
]
target_schema = next((p for p in schema_paths if os.path.exists(p)), "bphs_database_schema.json")

reader = BPHSDataReader(target_schema)
chatbot_engine = BPHSChatbotEngine(reader)


class BirthDetailsInput(BaseModel):
    name: str
    date_of_birth: str  # YYYY-MM-DD
    time_of_birth: str  # HH:MM or HH:MM:SS
    latitude: float
    longitude: float
    timezone_offset: float = 5.5  # Local civil time offset from UTC


class TransitRequestInput(BaseModel):
    latitude: float
    longitude: float
    timezone_offset: float = 5.5


class ChatbotQueryInput(BaseModel):
    user_question: str
    horoscope_data: Dict[str, Any]
    conversation_history: List[Dict[str, str]] = []
    mode: str = "online"


@app.get("/")
def root():
    return {
        "status": "Active",
        "system": "Brihat Parasara Hora Sastra Vedic Engine v4.0",
        "endpoints": ["/api/calculate-horoscope", "/api/live-transit-chart", "/api/chatbot-query"]
    }


@app.post("/api/calculate-horoscope")
def calculate_horoscope(details: BirthDetailsInput):
    """
    Accepts birth parameters, computes horoscope, 16 divisional charts, yogas, 
    dasha balance, and matches predictions from BPHS database.
    """
    try:
        # 1. Robust Time Parsing (HH:MM or HH:MM:SS)
        t_parts = details.time_of_birth.strip().split(":")
        hour = int(t_parts[0])
        minute = int(t_parts[1]) if len(t_parts) > 1 else 0
        second = int(t_parts[2]) if len(t_parts) > 2 else 0
        
        dob_date = datetime.datetime.strptime(details.date_of_birth.strip(), "%Y-%m-%d")
        local_dt = datetime.datetime(dob_date.year, dob_date.month, dob_date.day, hour, minute, second)
        if not (-14 <= details.timezone_offset <= 14):
            raise ValueError("timezone_offset must be between -14 and +14 hours")
        dt = local_dt - datetime.timedelta(hours=details.timezone_offset)  # Swiss Ephemeris requires UT

        # Require Swiss Ephemeris for chart-grade output; never silently label fallback as precision.
        from bphs_engine import HAS_SWISSEPH
        if not HAS_SWISSEPH:
            raise HTTPException(status_code=503, detail="Swiss Ephemeris is not installed. Install pyswisseph; approximate fallback is disabled for published chart calculations.")
        astro_res = compute_astronomical_positions(dt, details.latitude, details.longitude)
        ascendant_deg = astro_res["ascendant_longitude"]
        planets = astro_res["planets"]

        # 3. Calculate Shodashvarga for all planets
        shodashvarga_data = {p: ShodashvargaEngine.get_all_shodashvarga(deg) for p, deg in planets.items()}
        shodashvarga_data["Ascendant"] = ShodashvargaEngine.get_all_shodashvarga(ascendant_deg)

        # 4. Calculate Vimsopaka Strength Scores
        vimsopaka_scores = {
            p: VimsopakaEngine.calculate_vimsopaka_shodasa(p, deg)
            for p, deg in planets.items()
            if p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        }

        # 5. Detect Yogas
        yoga_engine = BPHSYogaEngine(planets, ascendant_deg)
        yogas_found = yoga_engine.detect_all_yogas()

        # 6. Calculate full Vimshottari Mahadasha/Antardasha/Pratyantardasha timeline
        dasha_info = VimshottariDashaEngine.calculate_dasha_balance(planets["Moon"])
        now_utc = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        dasha_timeline = vimshottari_timeline(planets["Moon"], dt, now_utc)

        # Current transit-to-natal contacts, using current UTC ephemeris positions
        transit_res = compute_astronomical_positions(now_utc, details.latitude, details.longitude)
        transit_analysis = transit_to_natal(planets, transit_res["planets"], ascendant_deg, now_utc.isoformat()+"Z")

        # 6.5. Compute Special Judgements (Stri Jataka & Nashta Jataka)
        stri_jataka_eval = BPHSSpecialJudgements.evaluate_stri_jataka(planets, ascendant_deg)
        nashta_jataka_trace = BPHSSpecialJudgements.trace_nashta_jataka(dt, ascendant_deg, planets)

        # 7. Package engine output
        engine_output = {
            "stri_jataka_evaluation": stri_jataka_eval,
            "nashta_jataka_tracing": nashta_jataka_trace,
            "ascendant_longitude": ascendant_deg,
            "ascendant_sign": int(ascendant_deg // 30) + 1,
            "planets": planets,
            "shodashvarga": shodashvarga_data,
            "vimsopaka_scores": vimsopaka_scores,
            "yogas": yogas_found,
            "dasha_at_birth": dasha_info,
            "vimshottari_timeline": dasha_timeline,
            "current_dasha": dasha_timeline.get("current", {}),
            "current_transit_analysis": transit_analysis,
            "precision_engine": astro_res.get("precision_engine", "Unknown"),
            "ayanamsa": astro_res.get("ayanamsa"),
            "house_system": "Whole Sign (sign-based bhava mapping)"
        }

        # 8. Query BPHS Database Reader for interpretations
        predictions = reader.process_engine_output(engine_output)

        return {
            "user_info": {
                "name": details.name,
                "dob": details.date_of_birth,
                "tob": details.time_of_birth,
                "timezone_offset": details.timezone_offset,
                "birth_datetime_utc": dt.isoformat()+"Z",
                "lat": details.latitude,
                "lon": details.longitude
            },
            "horoscope_calculations": engine_output,
            "bphs_predictions": predictions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/live-transit-chart")
def get_live_transit_chart(transit_req: TransitRequestInput):
    """
    Computes current live planetary transit positions (Gochar) and active transit yogas.
    """
    try:
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        astro_res = compute_astronomical_positions(now, transit_req.latitude, transit_req.longitude)
        
        return {
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S Live"),
            "transit_ascendant_deg": astro_res["ascendant_longitude"],
            "transit_ascendant_sign": int(astro_res["ascendant_longitude"] // 30) + 1,
            "transit_planets": astro_res["planets"],
            "precision_engine": astro_res.get("precision_engine", "Sidereal Math")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chatbot-status")
def chatbot_status():
    """Report whether online AI is configured; offline mode is always local."""
    return {"online_configured": bool(os.getenv("OPENAI_API_KEY", "").strip()), "offline_available": True, "model": os.getenv("OPENAI_MODEL", "gpt-4.1-mini")}


@app.post("/api/chatbot-query")
def query_bphs_chatbot(chat_input: ChatbotQueryInput):
    """
    Processes user questions against their birth chart context and returns BPHS-grounded AI prompt payload.
    """
    try:
        mode = (chat_input.mode or "online").strip().lower()
        if mode == "offline":
            return chatbot_engine.generate_offline_response_payload(
                user_question=chat_input.user_question,
                horoscope_data=chat_input.horoscope_data,
                history=chat_input.conversation_history
            )
        if mode != "online":
            raise HTTPException(status_code=400, detail="mode must be 'online' or 'offline'.")
        payload = chatbot_engine.generate_bot_response_payload(
            user_question=chat_input.user_question,
            horoscope_data=chat_input.horoscope_data,
            history=chat_input.conversation_history
        )
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/transit-to-natal")
def calculate_transit_to_natal(details: BirthDetailsInput):
    """Recompute current sidereal transits against supplied natal birth details."""
    try:
        parts=details.time_of_birth.strip().split(":")
        hh=int(parts[0]); mm=int(parts[1]) if len(parts)>1 else 0; ss=int(parts[2]) if len(parts)>2 else 0
        bd=datetime.datetime.strptime(details.date_of_birth.strip(), "%Y-%m-%d")
        local_dt=datetime.datetime(bd.year,bd.month,bd.day,hh,mm,ss)
        birth_utc=local_dt-datetime.timedelta(hours=details.timezone_offset)
        from bphs_engine import HAS_SWISSEPH
        if not HAS_SWISSEPH:
            raise HTTPException(status_code=503, detail="Swiss Ephemeris is required.")
        natal=compute_astronomical_positions(birth_utc,details.latitude,details.longitude)
        now=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        trans=compute_astronomical_positions(now,details.latitude,details.longitude)
        return transit_to_natal(natal["planets"],trans["planets"],natal["ascendant_longitude"],now.isoformat()+"Z")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=400,detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
