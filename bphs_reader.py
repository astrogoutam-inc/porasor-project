import json
import os
from typing import Dict, List, Any, Optional

class BPHSDataReader:
    """
    BPHS Data Reader Engine
    Acts as the bridge between calculation output (bphs_engine.py) 
    and the structured BPHS database (bphs_database_schema.json).
    """

    ORDINAL_MAP = {
        1: "1st", 2: "2nd", 3: "3rd", 4: "4th",
        5: "5th", 6: "6th", 7: "7th", 8: "8th",
        9: "9th", 10: "10th", 11: "11th", 12: "12th"
    }

    SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer",
        "Leo", "Virgo", "Libra", "Scorpio",
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    SIGN_RULERS = {
        0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon",
        4: "Sun", 5: "Mercury", 6: "Venus", 7: "Mars",
        8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter"
    }

    def __init__(self, json_path: str = "bphs_database_schema.json"):
        self.json_path = json_path
        self.data = self._load_database()

    def _load_database(self) -> Dict[str, Any]:
        search_paths = [
            self.json_path,
            os.path.join(os.path.dirname(__file__), self.json_path),
            f"/workspace/scratch/{os.path.basename(self.json_path)}",
            f"/workspace/artifacts/{os.path.basename(self.json_path)}"
        ]
        
        target_path = None
        for path in search_paths:
            if path and os.path.exists(path):
                target_path = path
                break
                
        if not target_path:
            raise FileNotFoundError(f"BPHS Database Schema file not found at search paths: {search_paths}")
        
        with open(target_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_bhava_phala(self, lord_house: int, placement_house: int) -> Dict[str, Any]:
        """
        Retrieves prediction when the lord of a specific house is placed in another house.
        """
        lord_ord = self.ORDINAL_MAP.get(lord_house, f"{lord_house}th")
        place_ord = self.ORDINAL_MAP.get(placement_house, f"{placement_house}th")

        candidate_keys = [
            f"lord_{lord_house}_in_{placement_house}",
            f"{lord_ord}_lord_in_{place_ord}_house",
            f"{lord_house}st_lord_in_{placement_house}th_house",
            f"{lord_house}nd_lord_in_{placement_house}th_house",
            f"{lord_house}rd_lord_in_{placement_house}th_house",
            f"{lord_house}th_lord_in_{placement_house}th_house",
            f"{lord_ord}_lord_in_{placement_house}th_house"
        ]

        matrix = self.data.get("modules", {}).get("bhava_phala_matrix_144", {}).get("combinations", {})
        if not matrix:
            matrix = self.data.get("bhava_phala_matrix_144", {}).get("combinations", {})

        matched_res = None
        matched_key = candidate_keys[0]
        for k in candidate_keys:
            if k in matrix:
                matched_res = matrix[k]
                matched_key = k
                break

        if matched_res:
            return {
                "key": matched_key,
                "lord_house": lord_house,
                "placement_house": placement_house,
                "bphs_chapter": matched_res.get("bphs_chapter", 24 + lord_house),
                "shloka_ref": matched_res.get("shloka_ref", ""),
                "title_bn": matched_res.get("title_bn", f"{lord_house}ম অধিপতি {placement_house}ম ভাবে"),
                "title_en": matched_res.get("title_en", f"{lord_ord} Lord in {place_ord} House"),
                "prediction_bn": matched_res.get("prediction_bn", ""),
                "prediction_en": matched_res.get("prediction_en", ""),
                "description_bn": matched_res.get("description_bn", matched_res.get("prediction_bn", "")),
                "description_en": matched_res.get("description_en", matched_res.get("prediction_en", ""))
            }

        fallback_bn = f"{lord_house}ম ভাবাধিপতি {placement_house}ম ভাবে অবস্থানের ফলে: শুভ বা মিশ্র প্রভাব সৃষ্টি হয়।"
        fallback_en = f"Lord of house {lord_house} placed in house {placement_house} gives functional influence according to BPHS."

        return {
            "key": matched_key,
            "lord_house": lord_house,
            "placement_house": placement_house,
            "bphs_chapter": 24 + lord_house,
            "title_bn": f"{lord_house}ম অধিপতি {placement_house}ম ভাবে",
            "title_en": f"{lord_ord} Lord in {place_ord} House",
            "prediction_bn": fallback_bn,
            "prediction_en": fallback_en,
            "description_bn": fallback_bn,
            "description_en": fallback_en,
            "source_status": "fallback_not_verified",
            "bphs_reference": None
        }

    def get_yoga_phala(self, yoga_key: str) -> Dict[str, Any]:
        yogas_db = self.data.get("modules", {}).get("yogas_database", {})
        if not yogas_db:
            yogas_db = self.data.get("yogas_database", {})

        for category, cat_data in yogas_db.items():
            if isinstance(cat_data, dict) and "yogas" in cat_data:
                if yoga_key in cat_data["yogas"]:
                    info = cat_data["yogas"][yoga_key]
                    return {
                        "yoga_key": yoga_key,
                        "category": category,
                        "name_bn": info.get("name_bn", yoga_key),
                        "name_en": info.get("name_en", yoga_key),
                        "condition_bn": info.get("condition", ""),
                        "condition_en": info.get("condition", ""),
                        "effects_bn": info.get("phala_bn", ""),
                        "effects_en": info.get("phala_en", ""),
                        "phala_bn": info.get("phala_bn", ""),
                        "phala_en": info.get("phala_en", "")
                    }

        return {
            "yoga_key": yoga_key,
            "name_bn": yoga_key.replace("_", " ").title(),
            "name_en": yoga_key.replace("_", " ").title(),
            "phala_bn": "এই যোগের নির্দিষ্ট ফল ডেটাবেসে যাচাইকৃতভাবে পাওয়া যায়নি।",
            "phala_en": "No verified interpretation for this yoga is present in the loaded database.",
            "source_status": "fallback_not_verified",
            "bphs_reference": None
        }

    def get_dasha_phala(self, mahadasha: str, antardasha: str) -> Dict[str, Any]:
        m_clean = str(mahadasha).strip().capitalize() if mahadasha else "Sun"
        a_clean = str(antardasha).strip().capitalize() if antardasha else "Sun"

        planet_map = {
            "Sun": "Sun", "Moon": "Moon", "Mars": "Mars", "Rahu": "Rahu",
            "Jupiter": "Jupiter", "Saturn": "Saturn", "Mercury": "Mercury",
            "Ketu": "Ketu", "Venus": "Venus"
        }
        m_key = planet_map.get(m_clean, m_clean)
        a_key = planet_map.get(a_clean, a_clean)

        dasha_db = self.data.get("modules", {}).get("dasha_phala_matrix", {}).get("antardasha_matrix", {})
        if not dasha_db:
            dasha_db = self.data.get("dasha_phala_matrix", {}).get("antardasha_matrix", {})

        maha_data = dasha_db.get(m_key, {})
        antar_data = maha_data.get(a_key, {})

        if antar_data:
            return {
                "mahadasha": m_key,
                "antardasha": a_key,
                "title_bn": antar_data.get("title_bn", f"{m_key}-এর মহাদশায় {a_key}-এর অন্তর্দশা"),
                "title_en": antar_data.get("title_en", f"{a_key} Antardasha in {m_key} Mahadasha"),
                "phala_bn": antar_data.get("phala_bn", ""),
                "phala_en": antar_data.get("phala_en", ""),
                "description_bn": antar_data.get("description_bn", antar_data.get("phala_bn", "")),
                "description_en": antar_data.get("description_en", antar_data.get("phala_en", "")),
                "remedy_bn": antar_data.get("remedy_bn", ""),
                "remedy_en": antar_data.get("remedy_en", ""),
                "bphs_reference": "BPHS Chapters 47-58 (Vimshottari Dasha Phala)"
            }

        return {
            "mahadasha": m_key,
            "antardasha": a_key,
            "title_bn": f"{m_key}-এর মহাদশায় {a_key}-এর অন্তর্দশা",
            "title_en": f"{a_key} Antardasha in {m_key} Mahadasha",
            "phala_bn": "এই নির্দিষ্ট দশা-যুগলের জন্য ডেটাবেসে যাচাইকৃত ফল পাওয়া যায়নি।",
            "phala_en": "No verified result for this Dasha pair is present in the loaded database.",
            "description_bn": "যাচাইকৃত ফল অনুপস্থিত; জন্মকুণ্ডলীর অধিপতি, অবস্থান ও বল আলাদাভাবে বিচার করতে হবে।",
            "description_en": "Verified result unavailable; judge house lordship, placement and strength separately.",
            "remedy_bn": "",
            "remedy_en": "",
            "source_status": "not_found",
            "bphs_reference": None
        }

    def get_shadbala_prediction(self, planet_name: str, shadbala_ratio: float) -> Dict[str, Any]:
        """
        Decodes BPHS Shadbala predictions for 7 planets based on ratio value (ratio = total / min_req).
        Tiers: Strong (>= 1.2), Moderate (0.9 - 1.2), Weak (< 0.9).
        """
        p_clean = planet_name.split()[0].title() if planet_name else "Sun"
        shad_db = self.data.get("modules", {}).get("shadbala_phala_matrix", {}).get("planets", {})
        if not shad_db:
            shad_db = self.data.get("shadbala_phala_matrix", {}).get("planets", {})

        p_data = shad_db.get(p_clean, {})

        tier_key = "strong" if shadbala_ratio >= 1.2 else ("moderate" if shadbala_ratio >= 0.9 else "weak")
        tier_info = p_data.get(tier_key, {})

        return {
            "planet": p_clean,
            "shadbala_ratio": round(shadbala_ratio, 2),
            "strength_tier": tier_key,
            "status_bn": tier_info.get("status_bn", ""),
            "status_en": tier_info.get("status_en", ""),
            "phala_bn": tier_info.get("phala_bn", ""),
            "phala_en": tier_info.get("phala_en", ""),
            "remedy_bn": tier_info.get("remedy_bn", ""),
            "remedy_en": tier_info.get("remedy_en", ""),
            "bphs_reference": "BPHS Chapters 27 & 28"
        }

    def get_bhavabala_prediction(self, house_num: int, bhavabala_rupas: float) -> Dict[str, Any]:
        """
        Decodes BPHS Bhava Bala predictions for 12 houses based on Rupas score.
        Tiers: Strong (>= 6.0 Rupas / >= 30 Virupas), Weak (< 6.0 Rupas).
        """
        h_key = f"House_{house_num}"
        bb_db = self.data.get("modules", {}).get("bhavabala_phala_matrix", {}).get("houses", {})
        if not bb_db:
            bb_db = self.data.get("bhavabala_phala_matrix", {}).get("houses", {})

        h_data = bb_db.get(h_key, {})

        is_strong = (bhavabala_rupas >= 6.0) or (bhavabala_rupas >= 30.0)
        tier_key = "strong" if is_strong else "weak"
        tier_info = h_data.get(tier_key, {})

        return {
            "house_number": house_num,
            "house_name_bn": h_data.get("house_name_bn", f"{house_num}ম ভাব"),
            "house_name_en": h_data.get("house_name_en", f"House {house_num}"),
            "rupas_score": round(bhavabala_rupas, 2),
            "strength_tier": tier_key,
            "status_bn": tier_info.get("status_bn", ""),
            "status_en": tier_info.get("status_en", ""),
            "phala_bn": tier_info.get("phala_bn", ""),
            "phala_en": tier_info.get("phala_en", ""),
            "remedy_bn": tier_info.get("remedy_bn", ""),
            "remedy_en": tier_info.get("remedy_en", ""),
            "bphs_reference": "BPHS Chapters 27 & 28"
        }

    def get_upapada_phala(
        self,
        ul_sign: str,
        occupying_planets_or_aspects: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Retrieves marital and life partner predictions based on Upapada Lagna (UL)
        and planets in or aspecting UL / 2nd from UL (BPHS Chapter 30).
        """
        if occupying_planets_or_aspects is None:
            occupying_planets_or_aspects = []

        ul_matrix = self.data.get("modules", {}).get("upapada_phala_matrix", {}).get("combinations", {})
        if not ul_matrix:
            ul_matrix = self.data.get("upapada_phala_matrix", {}).get("combinations", {})

        matched_predictions = []

        benefics = {"Jupiter", "Venus", "Mercury", "Moon"}
        malefics = {"Mars", "Saturn", "Rahu", "Ketu", "Sun"}

        found_benefics = [p for p in occupying_planets_or_aspects if p in benefics]
        found_malefics = [p for p in occupying_planets_or_aspects if p in malefics]

        if found_benefics and not found_malefics:
            if "benefics_in_ul_or_2nd" in ul_matrix:
                matched_predictions.append(ul_matrix["benefics_in_ul_or_2nd"])
        elif found_malefics and not found_benefics:
            if "malefics_in_ul_or_2nd" in ul_matrix:
                matched_predictions.append(ul_matrix["malefics_in_ul_or_2nd"])

        for p in occupying_planets_or_aspects:
            p_lower = str(p).lower()
            if "sun" in p_lower and "sun_in_upapada" in ul_matrix:
                matched_predictions.append(ul_matrix["sun_in_upapada"])
            elif "mars" in p_lower and "mars_in_upapada" in ul_matrix:
                matched_predictions.append(ul_matrix["mars_in_upapada"])
            elif "jupiter" in p_lower and "jupiter_in_upapada" in ul_matrix:
                matched_predictions.append(ul_matrix["jupiter_in_upapada"])
            elif "venus" in p_lower and "venus_in_upapada" in ul_matrix:
                matched_predictions.append(ul_matrix["venus_in_upapada"])
            elif ("saturn" in p_lower or "rahu" in p_lower or "ketu" in p_lower) and "saturn_rahu_ketu_in_upapada" in ul_matrix:
                matched_predictions.append(ul_matrix["saturn_rahu_ketu_in_upapada"])

        if not matched_predictions:
            matched_predictions.append({
                "key": "standard_upapada_prediction",
                "title_bn": f"উপপদ লগ্ন {ul_sign} বিচার",
                "title_en": f"Upapada Lagna in {ul_sign} Evaluation",
                "prediction_bn": f"উপপদ লগ্ন {ul_sign}-এ অবস্থান অনুযায়ী সাধারণ শুভ দাম্পত্য ফল ও অনুকূল পারিবারিক সম্পর্ক বজায় থাকবে। [BPHS Ch.30]",
                "prediction_en": f"Upapada Lagna in {ul_sign} maintains normal marital harmony and favorable domestic relations."
            })

        return {
            "ul_sign": ul_sign,
            "occupying_planets_or_aspects": occupying_planets_or_aspects,
            "predictions": matched_predictions,
            "bphs_reference": "BPHS Chapter 30 (Upa Pada)"
        }

    def get_maraka_and_arishta_analysis(self, planet_positions: Dict[str, Any], ascendant_sign: Any) -> Dict[str, Any]:
        """
        Determines Maraka places (2nd/7th houses) and Arishta Yogas according to BPHS Chapters 10, 11, 13 & 43-45.
        """
        if isinstance(ascendant_sign, (float, int)) and ascendant_sign > 12:
            asc_sign_idx = int(ascendant_sign // 30) % 12
        elif isinstance(ascendant_sign, int) and 1 <= ascendant_sign <= 12:
            asc_sign_idx = ascendant_sign - 1
        elif isinstance(ascendant_sign, int) and 0 <= ascendant_sign <= 11:
            asc_sign_idx = ascendant_sign
        else:
            asc_sign_idx = 0

        asc_sign_num = asc_sign_idx + 1
        asc_sign_name = self.SIGNS[asc_sign_idx]

        h2_lord = self.SIGN_RULERS[(asc_sign_idx + 1) % 12]
        h7_lord = self.SIGN_RULERS[(asc_sign_idx + 6) % 12]
        h6_lord = self.SIGN_RULERS[(asc_sign_idx + 5) % 12]
        h8_lord = self.SIGN_RULERS[(asc_sign_idx + 7) % 12]
        h12_lord = self.SIGN_RULERS[(asc_sign_idx + 11) % 12]
        lagna_lord = self.SIGN_RULERS[asc_sign_idx]

        primary_marakas = list(dict.fromkeys([h2_lord, h7_lord]))

        # Calculate house for each planet
        planet_houses = {}
        planet_signs = {}
        for p, pos in planet_positions.items():
            deg = pos.get('longitude', pos) if isinstance(pos, dict) else pos
            if isinstance(deg, (float, int)):
                s_idx = int(deg // 30) % 12
                h_num = ((s_idx - asc_sign_idx) % 12) + 1
                planet_houses[p] = h_num
                planet_signs[p] = s_idx

        planets_in_2nd = [p for p, h in planet_houses.items() if h == 2]
        planets_in_7th = [p for p, h in planet_houses.items() if h == 7]

        # Active Maraka planets
        active_marakas = []
        for p in primary_marakas:
            active_marakas.append({
                'planet': p,
                'role': 'Primary Marakesha (2nd/7th Lord)',
                'role_bn': f'{p} হলেন ২য়/৭ম ভাবাধিপতি (প্রধান মারকেশ)',
                'house_placed': planet_houses.get(p, 0)
            })

        for p in set(planets_in_2nd + planets_in_7th):
            if p not in primary_marakas and p not in ['Rahu', 'Ketu']:
                active_marakas.append({
                    'planet': p,
                    'role': 'Maraka Sthana Occupant',
                    'role_bn': f'{p} মারক স্থানে (২য়/৭ম ভাব) অবস্থানরত',
                    'house_placed': planet_houses.get(p, 0)
                })

        # Check Saturn Maraka association
        saturn_house = planet_houses.get('Saturn', 0)
        saturn_sign = planet_signs.get('Saturn', -1)
        is_saturn_maraka = (saturn_house in [2, 7]) or (saturn_sign == planet_signs.get(h2_lord, -2)) or (saturn_sign == planet_signs.get(h7_lord, -2))

        if is_saturn_maraka:
            active_marakas.append({
                'planet': 'Saturn',
                'role': 'Saturn Maraka Associate',
                'role_bn': 'শনি মারক স্থানে বা মারকেশের সাথে যুক্ত থাকায় পরম মারকত্বপ্রাপ্ত',
                'house_placed': saturn_house
            })

        # Arishta Yogas
        ma_db = self.data.get('modules', {}).get('maraka_and_arishta_matrix', {}).get('arishta_yogas', {})
        if not ma_db:
            ma_db = self.data.get('maraka_and_arishta_matrix', {}).get('arishta_yogas', {})

        arishta_detected = []

        # 1. Moon in Dusthana
        moon_house = planet_houses.get('Moon', 0)
        if moon_house in [6, 8, 12]:
            if 'moon_in_dusthana_arishta' in ma_db:
                arishta_detected.append(ma_db['moon_in_dusthana_arishta'])

        # 2. Lagna Lord in 8th
        lagna_lord_house = planet_houses.get(lagna_lord, 0)
        if lagna_lord_house == 8:
            if 'lagna_lord_in_8th_arishta' in ma_db:
                arishta_detected.append(ma_db['lagna_lord_in_8th_arishta'])

        # 3. Saturn Maraka
        if is_saturn_maraka and 'saturn_maraka_association' in ma_db:
            arishta_detected.append(ma_db['saturn_maraka_association'])

        # 4. Dusthana & Maraka conjunction
        dusthana_lords = [h6_lord, h8_lord, h12_lord]
        for dl in dusthana_lords:
            for ml in primary_marakas:
                if dl in planet_signs and ml in planet_signs and planet_signs[dl] == planet_signs[ml]:
                    if 'dusthana_maraka_conjunction' in ma_db:
                        if ma_db['dusthana_maraka_conjunction'] not in arishta_detected:
                            arishta_detected.append(ma_db['dusthana_maraka_conjunction'])

        return {
            'ascendant_sign_number': asc_sign_num,
            'ascendant_sign_name': asc_sign_name,
            'primary_maraka_lords': primary_marakas,
            'maraka_sthanas_info': {
                '2nd_house': {'lord': h2_lord, 'occupants': planets_in_2nd},
                '7th_house': {'lord': h7_lord, 'occupants': planets_in_7th}
            },
            'active_maraka_planets': active_marakas,
            'arishta_yogas_detected': arishta_detected,
            'bphs_reference': 'BPHS Chapters 10, 11, 13 & 43-45'
        }

    def process_engine_output(self, engine_output: Dict[str, Any]) -> Dict[str, Any]:
        predictions = {
            "bhava_predictions": [],
            "yoga_predictions": [],
            "dasha_predictions": [],
            "vimsopaka_analysis": [],
            "shadbala_predictions": [],
            "bhavabala_predictions": [],
            "upapada_predictions": {},
            "maraka_and_arishta_analysis": {}
        }

        planets = engine_output.get("planets", {})
        asc_deg = engine_output.get("ascendant_longitude", 0.0)
        asc_sign = int(asc_deg // 30) % 12

        # 1. Map Bhava Placements
        house_lords = {h: self.SIGN_RULERS[(asc_sign + h - 1) % 12] for h in range(1, 13)}
        for h_num in range(1, 13):
            lord = house_lords[h_num]
            lord_deg = planets.get(lord, 0.0)
            lord_sign = int(lord_deg // 30) % 12
            placement_house = ((lord_sign - asc_sign) % 12) + 1

            pred = self.get_bhava_phala(h_num, placement_house)
            predictions["bhava_predictions"].append(pred)

        # 2. Map Yogas
        yogas_found = engine_output.get("yogas", [])
        for y_str in yogas_found:
            key = "gajakesari_yoga" if "Gajakesari" in y_str else ("duradhara_yoga" if "Duradhara" in y_str else ("anapha_yoga" if "Anapha" in y_str else ("sunapha_yoga" if "Sunapha" in y_str else "kendra_trikona_raja_yoga")))
            y_pred = self.get_yoga_phala(key)
            predictions["yoga_predictions"].append(y_pred)

        # 3. Map Current Dasha
        current = engine_output.get("current_dasha", {}) or {}
        if current.get("mahadasha") and current.get("antardasha"):
            d_pred = self.get_dasha_phala(current["mahadasha"], current["antardasha"])
            d_pred["current_pratyantardasha"] = current.get("pratyantardasha")
            d_pred["period_start_utc"] = current.get("start_utc")
            d_pred["period_end_utc"] = current.get("end_utc")
            predictions["dasha_predictions"].append(d_pred)

        # 4. Map Vimsopaka
        vimsopaka = engine_output.get("vimsopaka_scores", {})
        for g, score in vimsopaka.items():
            status = "অত্যন্ত বলবান (Excellent)" if score >= 14 else ("শুভ (Good)" if score >= 10 else "সাধারণ (Moderate)")
            predictions["vimsopaka_analysis"].append({
                "graha": g,
                "score": score,
                "max": 20.0,
                "status": status
            })

        # 5. Map Shadbala & Bhavabala if available
        shadbala_data = engine_output.get("shadbala", {})
        if isinstance(shadbala_data, dict) and "shadbala_planets" in shadbala_data:
            for p_name, p_info in shadbala_data["shadbala_planets"].items():
                ratio = p_info.get("shadbala_ratio", 1.0)
                predictions["shadbala_predictions"].append(self.get_shadbala_prediction(p_name, ratio))

        bhavabala_data = engine_output.get("bhavabala", {})
        if isinstance(bhavabala_data, dict) and "bhava_bala_houses" in bhavabala_data:
            for h_code, h_info in bhavabala_data["bhava_bala_houses"].items():
                h_num = h_info.get("house_number", 1)
                rupas = h_info.get("total_bhava_bala_rupas", 6.0)
                predictions["bhavabala_predictions"].append(self.get_bhavabala_prediction(h_num, rupas))

        # 6. Map Upapada Predictions
        upapada_data = engine_output.get("upapada_marriage", {})
        if isinstance(upapada_data, dict):
            ul_sign = upapada_data.get("upapada_lagna_sign", "Aries")
            occ_planets = upapada_data.get("planets_in_2nd_from_upapada", [])
            predictions["upapada_predictions"] = self.get_upapada_phala(ul_sign, occ_planets)

        # 7. Map Maraka and Arishta Analysis
        if planets:
            predictions["maraka_and_arishta_analysis"] = self.get_maraka_and_arishta_analysis(planets, asc_deg)

        return predictions
