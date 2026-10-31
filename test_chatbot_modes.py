"""Local smoke tests for Online/Offline chatbot routing."""
from bphs_reader import BPHSDataReader
from bphs_chatbot import BPHSChatbotEngine


def sample_chart():
    return {
        "user_info": {"name": "Local Test", "dob": "1990-01-01"},
        "horoscope_calculations": {
            "ascendant_longitude": 100.0,
            "ascendant_sign": 4,
            "planets": {"Sun":280.0,"Moon":110.0,"Mars":30.0,"Mercury":290.0,"Jupiter":20.0,"Venus":200.0,"Saturn":250.0,"Rahu":50.0,"Ketu":230.0},
            "current_dasha": {"mahadasha":"Jupiter","antardasha":"Saturn","pratyantardasha":"Mercury","start_utc":"2026-01-01","end_utc":"2027-02-01"},
            "current_transit_analysis": {"transiting_planets_in_natal_whole_sign_houses":[{"transiting_planet":"Jupiter","house":10}],"parashari_transit_to_natal_planet_aspects":[]},
            "yogas": ["Smoke-test yoga"]
        },
        "bphs_predictions": {}
    }


def test_offline_mode_does_not_require_api_key():
    engine = BPHSChatbotEngine(BPHSDataReader("bphs_database_schema.json"))
    engine.api_key = ""
    result = engine.generate_offline_response_payload("আমার অর্থভাগ্য কেমন?", sample_chart())
    assert result["mode"] == "offline"
    assert "OFFLINE MODE" in result["bot_response"]
    assert isinstance(result["book_pages_retrieved"], list)


if __name__ == "__main__":
    test_offline_mode_does_not_require_api_key()
    print("PASS: offline mode works without an OpenAI API key")
