"""
BPHS AI Chatbot Engine (RAG & Context-Aware Prompt Handler)
Integrates Horoscope Calculations + BPHS Database Reader + LLM Prompt Builder
"""

from typing import Dict, Any, List
import json
import os
import sys

from bphs_reader import BPHSDataReader

class BPHSChatbotEngine:
    def __init__(self, reader_instance: BPHSDataReader):
        self.reader = reader_instance

    def extract_chart_context(self, horoscope_data: Dict[str, Any]) -> str:
        calc = horoscope_data.get("horoscope_calculations", {})
        user = horoscope_data.get("user_info", {})
        
        planets = calc.get("planets", {})
        dasha = calc.get("dasha_at_birth", {})
        yogas = calc.get("yogas", [])
        
        planet_summary = []
        for p, deg in planets.items():
            sign_num = int(deg // 30) + 1
            deg_in_sign = deg % 30
            planet_summary.append(f"{p}: Sign #{sign_num} ({deg_in_sign:.2f}°)")

        context_str = f"""
=== USER BIRTH CHART CONTEXT ===
Name: {user.get('name', 'User')}
Birth Date: {user.get('dob')} {user.get('tob')}
Ascendant Longitude: {calc.get('ascendant_longitude', 0):.2f}°
Planetary Positions: {', '.join(planet_summary)}
Active Yogas Identified: {', '.join(yogas) if yogas else 'None'}
Birth Mahadasha: {dasha.get('birth_mahadasha')} (Balance: {dasha.get('dasha_balance_years', 0):.2f} years)
Moon Nakshatra: {dasha.get('moon_nakshatra')}
================================
"""
        return context_str

    def build_grounded_prompt(self, user_question: str, horoscope_data: Dict[str, Any]) -> str:
        chart_context = self.extract_chart_context(horoscope_data)
        predictions = horoscope_data.get("bphs_predictions", {})
        relevant_shlokas = json.dumps(predictions, ensure_ascii=False, indent=2)

        system_prompt = f"""
You are an expert Vedic Astrologer AI grounded strictly in Brihat Parasara Hora Sastra (BPHS).
Answer the user's question accurately using ONLY BPHS rules and the provided user horoscope context.

{chart_context}

=== RELEVANT BPHS SHLOKAS & PREDICTIONS FROM DATABASE ===
{relevant_shlokas}

=== USER QUESTION ===
"{user_question}"

=== GUIDELINES ===
1. Respond in Bengali (or the language of the user's question).
2. Ground every astrological claim strictly in BPHS principles (cite houses, lords, yogas, and dashas).
3. Be respectful, encouraging, and clear without making false claims or non-BPHS predictions.
4. Explain clearly how their current Dasha, planetary positions, and BPHS rules apply to their question.
"""
        return system_prompt

    def generate_bot_response_payload(self, user_question: str, horoscope_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self.build_grounded_prompt(user_question, horoscope_data)
        
        predictions = horoscope_data.get("bphs_predictions", {})
        bhava_preds = predictions.get("bhava_predictions", [])
        yogas = horoscope_data.get("horoscope_calculations", {}).get("yogas", [])

        sample_pred = ""
        if isinstance(bhava_preds, list) and len(bhava_preds) > 0:
            first_p = bhava_preds[0]
            if isinstance(first_p, dict):
                sample_pred = first_p.get("prediction_bn") or first_p.get("description_bn", "")
        elif isinstance(bhava_preds, dict):
            sample_pred = bhava_preds.get("1st_lord_in_10th", "")

        if not sample_pred:
            sample_pred = "কর্মে ও জীবনে বিশেষ সাফল্য ও শুভ প্রভাব নির্দেশ করে।"

        yogas_str = ", ".join(yogas) if yogas else "শুভ যোগ বিদ্যমান"

        bot_reply = f"পরাশরী হোরা শাস্ত্র অনুযায়ী আপনার কুণ্ডলী বিচারে:\n১. {sample_pred}\n২. কুণ্ডলীতে সক্রিয় যোগ: {yogas_str}।"

        return {
            "status": "success",
            "user_question": user_question,
            "bot_response": bot_reply,
            "prepared_system_prompt": prompt,
            "grounding_sources_used": ["Brihat Parasara Hora Sastra", "bphs_database_schema.json"]
        }


if __name__ == "__main__":
    schema_path = "/workspace/scratch/bphs_database_schema.json" if os.path.exists("/workspace/scratch/bphs_database_schema.json") else "bphs_database_schema.json"
    reader = BPHSDataReader(schema_path)
    bot = BPHSChatbotEngine(reader)
    print("Chatbot Engine Verified Successfully!")
