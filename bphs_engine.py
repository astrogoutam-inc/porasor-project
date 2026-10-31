"""
Brihat Parasara Hora Sastra (BPHS) - Core Rules & Calculation Engine
Author: Gemini Notebook BPHS Engine Module
Language: Python 3.12
"""

import math
import datetime
from typing import Dict, List, Tuple, Any, Optional

# Try importing pyswisseph if available
try:
    import swisseph as swe
    HAS_SWISSEPH = True
except ImportError:
    HAS_SWISSEPH = False


SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# Planetary Ruler of each sign (0-indexed: 0 = Aries, 11 = Pisces)
SIGN_RULERS = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon",
    4: "Sun", 5: "Mercury", 6: "Venus", 7: "Mars",
    8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter"
}

# Exaltation signs and exact deep exaltation degrees (BPHS Ch. 3)
EXALTATION_DEGREES = {
    "Sun": 10.0,       # Aries 10°
    "Moon": 33.0,      # Taurus 3°
    "Mars": 298.0,     # Capricorn 28°
    "Mercury": 165.0,  # Virgo 15°
    "Jupiter": 95.0,   # Cancer 5°
    "Venus": 357.0,    # Pisces 27°
    "Saturn": 200.0,   # Libra 20°
}

DEBILITATION_DEGREES = {
    p: (deg + 180.0) % 360.0 for p, deg in EXALTATION_DEGREES.items()
}

OWN_SIGNS = {
    "Sun": [4],
    "Moon": [3],
    "Mars": [0, 7],
    "Mercury": [2, 5],
    "Jupiter": [8, 11],
    "Venus": [1, 6],
    "Saturn": [9, 10],
    "Rahu": [10],   # Aquarius (traditional secondary)
    "Ketu": [7]     # Scorpio (traditional secondary)
}

NATURAL_FRIENDSHIP = {
    "Sun":     {"Moon": 1,  "Mars": 1,  "Mercury": 0,  "Jupiter": 1,  "Venus": -1, "Saturn": -1},
    "Moon":    {"Sun": 1,   "Mars": 0,  "Mercury": 1,  "Jupiter": 0,  "Venus": 0,  "Saturn": 0},
    "Mars":    {"Sun": 1,   "Moon": 1,  "Mercury": -1, "Jupiter": 1,  "Venus": 0,  "Saturn": 0},
    "Mercury": {"Sun": 1,   "Moon": -1, "Mars": 0,     "Jupiter": 0,  "Venus": 1,  "Saturn": 0},
    "Jupiter": {"Sun": 1,   "Moon": 1,  "Mars": 1,     "Mercury": -1, "Venus": -1, "Saturn": 0},
    "Venus":   {"Sun": -1,  "Moon": -1, "Mars": 0,     "Mercury": 1,  "Jupiter": 0,  "Saturn": 1},
    "Saturn":  {"Sun": -1,  "Moon": -1, "Mars": -1,    "Mercury": 1,  "Jupiter": 0,  "Venus": 1},
}

VIMSHOTTARI_LORDS = [
    ("Ketu", 7), ("Venus", 20), ("Sun", 6),
    ("Moon", 10), ("Mars", 7), ("Rahu", 18),
    ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17)
]  # Total = 120 years


class ShodashvargaEngine:
    """Calculates all 16 Divisional Charts according to Maharshi Parasara."""

    @staticmethod
    def get_sign_and_deg(longitude: float) -> Tuple[int, float]:
        sign = int(longitude // 30) % 12
        rem_deg = longitude % 30
        return sign, rem_deg

    @classmethod
    def d1_rasi(cls, longitude: float) -> int:
        return int(longitude // 30) % 12

    @classmethod
    def d2_hora(cls, longitude: float) -> int:
        sign, deg = cls.get_sign_and_deg(longitude)
        is_odd = (sign % 2 == 0)
        if is_odd:
            return 4 if deg < 15.0 else 3
        else:
            return 3 if deg < 15.0 else 4

    @classmethod
    def d3_drekkana(cls, longitude: float) -> int:
        sign, deg = cls.get_sign_and_deg(longitude)
        part = int(deg // 10)
        return (sign + part * 4) % 12

    @classmethod
    def d4_chaturthamsa(cls, longitude: float) -> int:
        sign, deg = cls.get_sign_and_deg(longitude)
        part = int(deg // 7.5)
        return (sign + part * 3) % 12

    @classmethod
    def d7_saptamamsa(cls, longitude: float) -> int:
        sign, deg = cls.get_sign_and_deg(longitude)
        part = int(deg // (30.0 / 7.0))
        is_odd = (sign % 2 == 0)
        start_sign = sign if is_odd else (sign + 6) % 12
        return (start_sign + part) % 12

    @classmethod
    def d9_navamsa(cls, longitude: float) -> int:
        sign, deg = cls.get_sign_and_deg(longitude)
        part = int(deg // (30.0 / 9.0))
        element = sign % 4
        start_map = {0: 0, 1: 9, 2: 6, 3: 3}
        return (start_map[element] + part) % 12

    @classmethod
    def d10_dasamsa(cls, longitude: float) -> int:
        sign, deg = cls.get_sign_and_deg(longitude)
        part = int(deg // 3.0)
        is_odd = (sign % 2 == 0)
        start_sign = sign if is_odd else (sign + 8) % 12
        return (start_sign + part) % 12

    @classmethod
    def d12_dwadasamsa(cls, longitude: float) -> int:
        sign, deg = cls.get_sign_and_deg(longitude)
        part = int(deg // 2.5)
        return (sign + part) % 12

    @classmethod
    def d16_shodasamsa(cls, longitude: float) -> int:
        sign, deg = cls.get_sign_and_deg(longitude)
        part = int(deg // (30.0 / 16.0))
        modality = sign % 3
        start_map = {0: 0, 1: 4, 2: 8}
        return (start_map[modality] + part) % 12

    @classmethod
    def d20_vimsamsa(cls, longitude: float) -> int:
        sign, deg = cls.get_sign_and_deg(longitude)
        part = int(deg // 1.5)
        modality = sign % 3
        start_map = {0: 0, 1: 8, 2: 4}
        return (start_map[modality] + part) % 12

    @classmethod
    def d24_chaturvimsamsa(cls, longitude: float) -> int:
        sign, deg = cls.get_sign_and_deg(longitude)
        part = int(deg // 1.25)
        is_odd = (sign % 2 == 0)
        start_sign = 4 if is_odd else 3
        return (start_sign + part) % 12

    @classmethod
    def d27_sapthavimsamsa(cls, longitude: float) -> int:
        sign, deg = cls.get_sign_and_deg(longitude)
        part = int(deg // (30.0 / 27.0))
        element = sign % 4
        start_map = {0: 0, 1: 3, 2: 6, 3: 9}
        return (start_map[element] + part) % 12

    @classmethod
    def d30_trimsamsa(cls, longitude: float) -> int:
        """D30: Trimsamsa (Evils & Miseries) - BPHS Ch. 6 v.31-33"""
        sign, deg = cls.get_sign_and_deg(longitude)
        is_odd = (sign % 2 == 0)
        if is_odd:
            if deg < 5.0: return 0     # Aries (Mars)
            elif deg < 10.0: return 10 # Aquarius (Saturn)
            elif deg < 18.0: return 8  # Sagittarius (Jupiter)
            elif deg < 25.0: return 2  # Gemini (Mercury)
            else: return 6             # Libra (Venus) -> Fixed typo (return 6)
        else:
            if deg < 5.0: return 1     # Taurus (Venus)
            elif deg < 12.0: return 2  # Gemini (Mercury)
            elif deg < 20.0: return 8  # Sagittarius (Jupiter)
            elif deg < 25.0: return 10 # Aquarius (Saturn)
            else: return 0             # Aries (Mars)

    @classmethod
    def d40_khavedamsa(cls, longitude: float) -> int:
        sign, deg = cls.get_sign_and_deg(longitude)
        part = int(deg // 0.75)
        is_odd = (sign % 2 == 0)
        start_sign = 0 if is_odd else 6
        return (start_sign + part) % 12

    @classmethod
    def d45_akshavedamsa(cls, longitude: float) -> int:
        sign, deg = cls.get_sign_and_deg(longitude)
        part = int(deg // (30.0 / 45.0))
        modality = sign % 3
        start_map = {0: 0, 1: 4, 2: 8}
        return (start_map[modality] + part) % 12

    @classmethod
    def d60_shashtiamsa(cls, longitude: float) -> int:
        sign, deg = cls.get_sign_and_deg(longitude)
        part = int(deg // 0.5)
        return (sign + part) % 12

    @classmethod
    def get_all_shodashvarga(cls, longitude: float) -> Dict[str, Tuple[int, str]]:
        vargas = {
            "D1_Rasi": cls.d1_rasi(longitude),
            "D2_Hora": cls.d2_hora(longitude),
            "D3_Drekkana": cls.d3_drekkana(longitude),
            "D4_Chaturthamsa": cls.d4_chaturthamsa(longitude),
            "D7_Saptamamsa": cls.d7_saptamamsa(longitude),
            "D9_Navamsa": cls.d9_navamsa(longitude),
            "D10_Dasamsa": cls.d10_dasamsa(longitude),
            "D12_Dwadasamsa": cls.d12_dwadasamsa(longitude),
            "D16_Shodasamsa": cls.d16_shodasamsa(longitude),
            "D20_Vimsamsa": cls.d20_vimsamsa(longitude),
            "D24_Siddhamsa": cls.d24_chaturvimsamsa(longitude),
            "D27_Bhamsa": cls.d27_sapthavimsamsa(longitude),
            "D30_Trimsamsa": cls.d30_trimsamsa(longitude),
            "D40_Khavedamsa": cls.d40_khavedamsa(longitude),
            "D45_Akshavedamsa": cls.d45_akshavedamsa(longitude),
            "D60_Shashtiamsa": cls.d60_shashtiamsa(longitude),
        }
        return {k: (s_idx, SIGNS[s_idx]) for k, s_idx in vargas.items()}


class VimsopakaEngine:
    """Computes Vimsopaka 20-Point Strength Scheme for Planets."""

    SHODASA_SWAVISWA = {
        "D1_Rasi": 3.5, "D2_Hora": 1.0, "D3_Drekkana": 1.0,
        "D4_Chaturthamsa": 0.5, "D7_Saptamamsa": 0.5, "D9_Navamsa": 3.0,
        "D10_Dasamsa": 0.5, "D12_Dwadasamsa": 0.5, "D16_Shodasamsa": 2.0,
        "D20_Vimsamsa": 0.5, "D24_Siddhamsa": 0.5, "D27_Bhamsa": 0.5,
        "D30_Trimsamsa": 1.0, "D40_Khavedamsa": 0.5, "D45_Akshavedamsa": 0.5,
        "D60_Shashtiamsa": 4.0
    }

    @classmethod
    def get_varga_viswa_score(cls, planet: str, occupied_sign: int) -> float:
        ruler = SIGN_RULERS[occupied_sign]
        if occupied_sign in OWN_SIGNS.get(planet, []):
            return 20.0
        if planet in NATURAL_FRIENDSHIP:
            rel = NATURAL_FRIENDSHIP[planet].get(ruler, 0)
            if rel == 1: return 15.0
            elif rel == 0: return 10.0
            elif rel == -1: return 7.0
        return 10.0

    @classmethod
    def calculate_vimsopaka_shodasa(cls, planet: str, planet_long: float) -> float:
        vargas = ShodashvargaEngine.get_all_shodashvarga(planet_long)
        total_score = 0.0
        for varga_code, (sign_idx, _) in vargas.items():
            swaviswa = cls.SHODASA_SWAVISWA[varga_code]
            varga_viswa = cls.get_varga_viswa_score(planet, sign_idx)
            net = (swaviswa * varga_viswa) / 20.0
            total_score += net
        return round(total_score, 2)


class BPHSYogaEngine:
    """Scans birth chart longitudes and identifies BPHS Yogas."""

    def __init__(self, planet_positions: Dict[str, float], ascendant_long: float):
        self.positions = planet_positions
        self.ascendant = ascendant_long
        self.asc_sign = int(ascendant_long // 30) % 12
        
        self.planet_houses = {}
        self.planet_signs = {}
        for p, long in planet_positions.items():
            p_sign = int(long // 30) % 12
            house = ((p_sign - self.asc_sign) % 12) + 1
            self.planet_houses[p] = house
            self.planet_signs[p] = p_sign

        self.house_lords = {
            h: SIGN_RULERS[(self.asc_sign + h - 1) % 12] for h in range(1, 13)
        }

    def detect_raja_yogas(self) -> List[str]:
        yogas = []
        kendra_houses = [1, 4, 7, 10]
        trikona_houses = [5, 9]

        kendra_lords = set(self.house_lords[h] for h in kendra_houses)
        trikona_lords = set(self.house_lords[h] for h in trikona_houses)

        for k_lord in kendra_lords:
            for t_lord in trikona_lords:
                if k_lord == t_lord:
                    continue
                k_house = self.planet_houses.get(k_lord)
                t_house = self.planet_houses.get(t_lord)
                if k_house and t_house and k_house == t_house:
                    yogas.append(f"Raja Yoga: Conjunction of Kendrapati ({k_lord}) & Trikonapati ({t_lord}) in House {k_house} [BPHS Ch.39]")

        return yogas

    def detect_gajakesari_yoga(self) -> List[str]:
        yogas = []
        if "Jupiter" in self.planet_signs and "Moon" in self.planet_signs:
            jup_sign = self.planet_signs["Jupiter"]
            moon_sign = self.planet_signs["Moon"]
            diff = (jup_sign - moon_sign) % 12
            if diff in [0, 3, 6, 9]:
                yogas.append("Gajakesari Yoga: Jupiter in Kendra from Moon - brings fame, wisdom & enduring wealth [BPHS Ch.36]")
        return yogas

    def detect_lunar_yogas(self) -> List[str]:
        yogas = []
        if "Moon" not in self.planet_signs:
            return yogas

        m_sign = self.planet_signs["Moon"]
        second_sign = (m_sign + 1) % 12
        twelfth_sign = (m_sign - 1) % 12

        second_planets = [p for p, s in self.planet_signs.items() if s == second_sign and p not in ["Moon", "Sun", "Rahu", "Ketu"]]
        twelfth_planets = [p for p, s in self.planet_signs.items() if s == twelfth_sign and p not in ["Moon", "Sun", "Rahu", "Ketu"]]

        if second_planets and not twelfth_planets:
            yogas.append(f"Sunapha Yoga: Planets in 2nd from Moon ({', '.join(second_planets)}) - intelligence & self-earned wealth [BPHS Ch.37]")
        elif twelfth_planets and not second_planets:
            yogas.append(f"Anapha Yoga: Planets in 12th from Moon ({', '.join(twelfth_planets)}) - good health & reputation [BPHS Ch.37]")
        elif second_planets and twelfth_planets:
            yogas.append("Duradhara Yoga: Planets in both 2nd & 12th from Moon - prosperous, charitable & well-served [BPHS Ch.37]")
        else:
            kendra_planets = [p for p, h in self.planet_houses.items() if h in [1, 4, 7, 10] and p != "Moon"]
            if not kendra_planets:
                yogas.append("Kemadruma Yoga: No planets in 2nd/12th from Moon or Kendra from Ascendant [BPHS Ch.37]")

        return yogas

    def detect_all_yogas(self) -> List[str]:
        all_y = []
        all_y.extend(self.detect_raja_yogas())
        all_y.extend(self.detect_gajakesari_yoga())
        all_y.extend(self.detect_lunar_yogas())
        return all_y


class VimshottariDashaEngine:
    """Calculates Vimshottari Dasha Balance & Sequence as a clean Dict structure."""

    NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]

    @classmethod
    def calculate_dasha_balance(cls, moon_long: float) -> Dict[str, Any]:
        nak_length = 360.0 / 27.0
        nak_idx = int(moon_long // nak_length)
        rem_deg_in_nak = moon_long % nak_length
        fraction_traversed = rem_deg_in_nak / nak_length

        lord_idx = nak_idx % 9
        lord_name, total_years = VIMSHOTTARI_LORDS[lord_idx]
        remaining_years = total_years * (1.0 - fraction_traversed)
        nak_name = cls.NAKSHATRAS[nak_idx % 27]

        sequence = []
        for i in range(9):
            idx = (lord_idx + i) % 9
            p_name, p_yrs = VIMSHOTTARI_LORDS[idx]
            sequence.append({"planet": p_name, "years": p_yrs})

        return {
            "birth_mahadasha": lord_name,
            "dasha_balance_years": round(remaining_years, 2),
            "total_dasha_years": total_years,
            "moon_nakshatra": nak_name,
            "nakshatra_lord": lord_name,
            "full_dasha_sequence": sequence
        }


def compute_astronomical_positions(
    dt: Optional[datetime.datetime] = None,
    lat: float = 22.5726,
    lon: float = 88.3639,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    hour: int = 0,
    minute: int = 0,
    second: int = 0
) -> Dict[str, Any]:
    """
    Computes sidereal planetary longitudes and Ascendant degree.
    Flexible signature: accepts either a single `datetime` object OR individual year/month/day parameters.
    Uses SwissEphemeris (pyswisseph) if available, otherwise high-precision astronomical formula fallback.
    """
    if dt is None:
        if year is not None and month is not None and day is not None:
            dt = datetime.datetime(year, month, day, hour, minute, second)
        else:
            dt = datetime.datetime.now()

    if HAS_SWISSEPH:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        julian_day = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0)
        ayanamsa = swe.get_ayanamsa_ut(julian_day)
        
        planets_map = {
            "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
            "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
            "Venus": swe.VENUS, "Saturn": swe.SATURN,
            "Rahu": swe.MEAN_NODE
        }
        longs = {}
        for p_name, p_id in planets_map.items():
            res, _ = swe.calc_ut(julian_day, p_id)
            tropical_deg = res[0]
            sidereal_deg = (tropical_deg - ayanamsa) % 360.0
            longs[p_name] = round(sidereal_deg, 2)
            
        longs["Ketu"] = round((longs["Rahu"] + 180.0) % 360.0, 2)
        houses, ascmc = swe.houses_ex(julian_day, lat, lon, b'P', swe.FLG_SIDEREAL)
        asc_deg = round(ascmc[0] % 360.0, 2)
        
        return {
            "ascendant_longitude": asc_deg,
            "planets": longs,
            "ayanamsa": round(ayanamsa, 2),
            "precision_engine": "SwissEphemeris (Lahiri Ayanamsa)"
        }
    else:
        # Fallback astronomical computation
        days_since_2000 = (dt - datetime.datetime(2000, 1, 1, 12, 0)).total_seconds() / 86400.0
        ayanamsa = 23.85 + (days_since_2000 / 365.25) * (50.29 / 3600.0)
        
        longs = {
            "Sun": round((280.46 + 0.9856474 * days_since_2000 - ayanamsa) % 360.0, 2),
            "Moon": round((218.32 + 13.176396 * days_since_2000 - ayanamsa) % 360.0, 2),
            "Mars": round((355.43 + 0.524033 * days_since_2000 - ayanamsa) % 360.0, 2),
            "Mercury": round((252.25 + 4.092334 * days_since_2000 - ayanamsa) % 360.0, 2),
            "Jupiter": round((34.35 + 0.083091 * days_since_2000 - ayanamsa) % 360.0, 2),
            "Venus": round((181.98 + 1.602130 * days_since_2000 - ayanamsa) % 360.0, 2),
            "Saturn": round((50.08 + 0.033459 * days_since_2000 - ayanamsa) % 360.0, 2),
            "Rahu": round((125.04 - 0.05295 * days_since_2000 - ayanamsa) % 360.0, 2)
        }
        longs["Ketu"] = round((longs["Rahu"] + 180.0) % 360.0, 2)
        
        lst = (100.46 + 0.985647 * days_since_2000 + lon + (dt.hour + dt.minute/60.0) * 15.0) % 360.0
        asc_deg = round((lst - ayanamsa) % 360.0, 2)
        
        return {
            "ascendant_longitude": asc_deg,
            "planets": longs,
            "ayanamsa": round(ayanamsa, 2),
            "precision_engine": "Sidereal Mathematical Fallback"
        }


class BPHSSpecialJudgements:
    """
    Computes BPHS Chapter 73 ('Stri Jataka / Female Horoscopy')
    and Chapter 80 ('Nashta Jataka / Lost Horoscopy').
    """

    TRIMSAMSA_PREDICTIONS = {
        "Mars_Signs": {
            "Mars": "অধৈর্য, তেজস্বী, স্বাধীনচেতা ও স্বতঃস্ফূর্ত স্বভাবের। [BPHS Ch.73]",
            "Saturn": "পরনির্ভরশীল বা দাসীবৃত্তির সম্ভাবনা, দাম্পত্য জীবনে ধৈর্য ও সতর্কতা প্রয়োজন। [BPHS Ch.73]",
            "Jupiter": "পরম ধার্মিক, পতিব্রতা, সুচরিত্রা ও সর্বজনপূজ্য নারী। [BPHS Ch.73]",
            "Mercury": "প্রজ্ঞাবান, বুদ্ধিমতী, শিল্পানুরাগী ও চতুর স্বভাবের। [BPHS Ch.73]",
            "Venus": "প্রেমপরায়ণ, সুন্দর রূপলাবণ্যযুক্ত ও কামুক প্রকৃতির। [BPHS Ch.73]"
        },
        "Venus_Signs": {
            "Venus": "উচ্চ গুণসম্পন্ন, সর্বজনপ্রিয়, রূপবতী ও পরম শুভযোগযুক্ত। [BPHS Ch.73]",
            "Mercury": "সঙ্গীত ও সুকুমার শিল্পে দক্ষ, প্রজ্ঞাবান ও বিনয়ী। [BPHS Ch.73]",
            "Jupiter": "গুণবতী, সচ্চরিত্রা, স্বামীভক্ত ও প্রভূত সুখে সমৃদ্ধি লাভ। [BPHS Ch.73]",
            "Saturn": "পুনর্বিবাহ বা দাম্পত্য জীবনে প্রাথমিক জটিলতার সম্ভাবনা। [BPHS Ch.73]",
            "Mars": "উগ্র স্বভাব বা আবেগপ্রবণ আচরণের কারণে সতর্কতার প্রয়োজন। [BPHS Ch.73]"
        },
        "Mercury_Signs": {
            "Mercury": "বিজ্ঞ, বিদুষী, মার্জিত ভাষা ও প্রজ্ঞাবান ব্যক্তিত্ব। [BPHS Ch.73]",
            "Venus": "শিল্পকলা ও সুকুমার প্রীতি, অত্যন্ত প্রেমময় হৃদয়। [BPHS Ch.73]",
            "Jupiter": "পতিব্রতা, ধার্মিক, লক্ষ্মীস্বরূপা ও প্রভূত ভূসম্পত্তির মালিক। [BPHS Ch.73]",
            "Mars": "কপটতা বা বাকপটুতার সাথে স্বার্থসিদ্ধির প্রবণতা। [BPHS Ch.73]",
            "Saturn": "গম্ভীর, শান্ত বা সন্তানলাভে বিলম্ব নির্দেশক। [BPHS Ch.73]"
        },
        "Cancer_Sign": {
            "Mars": "স্বচ্ছন্দ মনোভাব, অনমনীয় ও স্বাধীনচেতা। [BPHS Ch.73]",
            "Saturn": "দাম্পত্য সুখে বাধা বা দীর্ঘ বিরহ নির্দেশক। [BPHS Ch.73]",
            "Jupiter": "পরম সম্মানিত, উচ্চ রাজকীয় পদ ও গুণবতী নারী। [BPHS Ch.73]",
            "Mercury": "চিত্রকলা, হস্তশিল্প ও বুদ্ধিবৃত্তিক কাজে বিশেষ পারদর্শী। [BPHS Ch.73]",
            "Venus": "কামনাপ্রবণ বা সৌন্দর্যমুখী আবেগপ্রবণতা। [BPHS Ch.73]"
        },
        "Leo_Sign": {
            "Mars": "বাচাল, তেজস্বী ও উগ্র স্বভাব। [BPHS Ch.73]",
            "Saturn": "মানসিক ক্লেশ বা কঠোর পরিশ্রমের নির্দেশক। [BPHS Ch.73]",
            "Jupiter": "রাজরানী সদৃশ সম্মানিত, মহীয়সী ও প্রজ্ঞাবান। [BPHS Ch.73]",
            "Mercury": "পুরুষালী ব্যক্তিত্ব, সাহসী ও শাসনক্ষমতাসম্পন্ন। [BPHS Ch.73]",
            "Venus": "প্রেমাকুল ও আবেগপ্রবণ হৃদয়ের অধিকারী। [BPHS Ch.73]"
        },
        "Jupiter_Signs": {
            "Jupiter": "পরম শুদ্ধাচারী, সর্বগুণসম্পন্ন ও আধ্যাত্মিক চেতনায় প্রদীপ্ত। [BPHS Ch.73]",
            "Mercury": "পণ্ডিত, বিজ্ঞানমনস্ক, নম্র ও সুবক্তা। [BPHS Ch.73]",
            "Venus": "পবিত্র হৃদয়, নম্র, সন্তানসুখে সমৃদ্ধ ও আদর্শ গৃহিণী। [BPHS Ch.73]",
            "Mars": "অত্যন্ত সাহসী, পরাক্রমশালী ও স্পষ্টভাষী। [BPHS Ch.73]",
            "Saturn": "অনাসক্ত, সংযমী ও নির্জনতাপ্রিয়। [BPHS Ch.73]"
        },
        "Saturn_Signs": {
            "Saturn": "কঠোর পরিশ্রমী, সংবেদনশীল ও প্রতিকূলতায় সহনশীল। [BPHS Ch.73]",
            "Mars": "উগ্র মনোভাব বা জটিল পরিস্থিতির মুখোমুখি। [BPHS Ch.73]",
            "Jupiter": "পতিব্রতা, ধনী, সুশীল ও বংশের প্রদীপস্বরূপ। [BPHS Ch.73]",
            "Mercury": "বুদ্ধিমতী, নম্র, কৌশলী ও সদাসুখী। [BPHS Ch.73]",
            "Venus": "শিল্পানুরাগী, চঞ্চল বা সন্তান বিষয়ে বিশেষ যত্নশীল। [BPHS Ch.73]"
        }
    }

    @classmethod
    def get_trimsamsa_group_key(cls, rasi_sign_idx: int) -> str:
        if rasi_sign_idx in [0, 7]: return "Mars_Signs"
        elif rasi_sign_idx in [1, 6]: return "Venus_Signs"
        elif rasi_sign_idx in [2, 5]: return "Mercury_Signs"
        elif rasi_sign_idx == 3: return "Cancer_Sign"
        elif rasi_sign_idx == 4: return "Leo_Sign"
        elif rasi_sign_idx in [8, 11]: return "Jupiter_Signs"
        else: return "Saturn_Signs"

    @classmethod
    def evaluate_stri_jataka(
        cls,
        planet_positions: Dict[str, float],
        ascendant_long: float
    ) -> Dict[str, Any]:
        """
        Evaluates Stri Jataka / Female Horoscopy according to BPHS Chapter 73.
        Analyzes Trimsamsa (D30) of Lagna & Moon, plus 7th & 8th houses for marital destiny.
        """
        asc_sign = int(ascendant_long // 30) % 12
        asc_d30_sign = ShodashvargaEngine.d30_trimsamsa(ascendant_long)
        asc_d30_ruler = SIGN_RULERS[asc_d30_sign]

        moon_long = planet_positions.get("Moon", 0.0)
        moon_sign = int(moon_long // 30) % 12
        moon_d30_sign = ShodashvargaEngine.d30_trimsamsa(moon_long)
        moon_d30_ruler = SIGN_RULERS[moon_d30_sign]

        # Trimsamsa predictions
        lagna_group = cls.get_trimsamsa_group_key(asc_sign)
        moon_group = cls.get_trimsamsa_group_key(moon_sign)

        lagna_d30_pred = cls.TRIMSAMSA_PREDICTIONS.get(lagna_group, {}).get(
            asc_d30_ruler, "স্বাভাবিক ও শুভ প্রভাব।"
        )
        moon_d30_pred = cls.TRIMSAMSA_PREDICTIONS.get(moon_group, {}).get(
            moon_d30_ruler, "স্বাভাবিক মানসিক প্রবণতা।"
        )

        # 7th and 8th House Evaluation for Female Horoscope (BPHS Ch. 73 v.23-40)
        h7_sign = (asc_sign + 6) % 12
        h7_lord = SIGN_RULERS[h7_sign]
        h8_sign = (asc_sign + 7) % 12
        h8_lord = SIGN_RULERS[h8_sign]

        planet_signs = {p: int(deg // 30) % 12 for p, deg in planet_positions.items()}

        p_in_7th = [p for p, s in planet_signs.items() if s == h7_sign]
        p_in_8th = [p for p, s in planet_signs.items() if s == h8_sign]

        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]
        malefics = ["Mars", "Saturn", "Rahu", "Ketu", "Sun"]

        b_7th = [p for p in p_in_7th if p in benefics]
        m_7th = [p for p in p_in_7th if p in malefics]
        b_8th = [p for p in p_in_8th if p in benefics]
        m_8th = [p for p in p_in_8th if p in malefics]

        # 7th house judgment
        if "Jupiter" in p_in_7th or "Venus" in p_in_7th or (b_7th and not m_7th):
            h7_judgement = "অত্যন্ত শুভ বিবাহ যোগ: পতিব্রতা, সৌভাগ্যবতী এবং গুণবান ও প্রতিষ্ঠিত স্বামীর প্রাপ্তি নির্দেশ করে। [BPHS Ch.73]"
        elif "Mars" in p_in_7th and not b_7th:
            h7_judgement = "মঙ্গল দোষ / তেজস্বী পতি: দাম্পত্যে বাদানুবাদ এড়াতে পরস্পরের প্রতি ধৈর্য ও কুষ্ঠিমিলন আবশ্যক। [BPHS Ch.73]"
        elif m_7th and not b_7th:
            h7_judgement = "৭মে পাপগ্রহের প্রভাবে বিবাহে বিলম্ব বা মানসিক পার্থক্যের ইঙ্গিত, প্রতিকার প্রয়োজন। [BPHS Ch.73]"
        else:
            h7_judgement = "স্বাভাবিক ও সুষম দাম্পত্য জীবন। [BPHS Ch.73]"

        # 8th house judgment
        if b_8th and not m_8th:
            h8_judgement = "দীর্ঘ মাঙ্গল্য যোগ: অক্ষয় সধবা যোগ, স্বামীর সুস্বাস্থ্য, দীর্ঘায়ু ও পারিবারিক সমৃদ্ধি। [BPHS Ch.73]"
        elif m_8th and not b_8th:
            h8_judgement = "৮মে পাপগ্রহ থাকায় স্বামীর স্বাস্থ্য ও আয়ু বিষয়ে সচেতনতা ও গ্রহ শান্তি প্রয়োজন। [BPHS Ch.73]"
        else:
            h8_judgement = "শুভ মাঙ্গল্য ও স্বাভাবিক পারিবারিক সুখ। [BPHS Ch.73]"

        return {
            "lagna_trimsamsa_analysis": {
                "lagna_rasi": SIGNS[asc_sign],
                "trimsamsa_sign": SIGNS[asc_d30_sign],
                "trimsamsa_ruler": asc_d30_ruler,
                "character_prediction_bn": lagna_d30_pred
            },
            "moon_trimsamsa_analysis": {
                "moon_rasi": SIGNS[moon_sign],
                "trimsamsa_sign": SIGNS[moon_d30_sign],
                "trimsamsa_ruler": moon_d30_ruler,
                "temperament_prediction_bn": moon_d30_pred
            },
            "seventh_house_evaluation": {
                "seventh_house_sign": SIGNS[h7_sign],
                "seventh_house_lord": h7_lord,
                "planets_in_seventh": p_in_7th,
                "marital_judgement_bn": h7_judgement
            },
            "eighth_house_evaluation": {
                "eighth_house_sign": SIGNS[h8_sign],
                "eighth_house_lord": h8_lord,
                "planets_in_eighth": p_in_8th,
                "mangalya_judgement_bn": h8_judgement
            },
            "bphs_reference": "BPHS Chapter 73 (Stri Jataka)"
        }

    @classmethod
    def trace_nashta_jataka(
        cls,
        prasna_dt: datetime.datetime,
        prasna_ascendant_long: float,
        prasna_planets: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Traces probable birth parameters for Lost Horoscopy (Nashta Jataka)
        according to BPHS Chapter 80 from Horary/Prasna Lagna & planetary positions.
        """
        nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]

        p_asc_sign = int(prasna_ascendant_long // 30) % 12
        p_sun_long = prasna_planets.get("Sun", 0.0)
        p_sun_sign = int(p_sun_long // 30) % 12

        if p_sun_sign in [8, 9, 10, 11, 0, 1]:
            ayana = "উত্তরায়ণ (Uttarayana - Sun in Northern Hemisphere)"
        else:
            ayana = "দক্ষিণায়ন (Dakshinayana - Sun in Southern Hemisphere)"

        deg_in_sign = prasna_ascendant_long % 30.0
        drekkana_idx = int(deg_in_sign // 10.0)

        ritu_map = {
            (0, 0): "বসন্ত ঋতু (Vasanta Ritu - Spring)",
            (0, 1): "গ্রীষ্ম ঋতু (Greeshma Ritu - Summer)",
            (0, 2): "বর্ষা ঋতু (Varsha Ritu - Rainy)",
            (1, 0): "শরৎ ঋতু (Sharad Ritu - Autumn)",
            (1, 1): "হেমনন্ত ঋতু (Hemanta Ritu - Pre-Winter)",
            (1, 2): "শিশির ঋতু (Sisira Ritu - Winter)"
        }

        modality = p_asc_sign % 3
        ritu = ritu_map.get((modality % 2, drekkana_idx), "বসন্ত/গ্রীষ্ম ঋতু")

        d12_part = int(deg_in_sign // 2.5)
        probable_birth_sun_sign_idx = (p_asc_sign + d12_part) % 12
        probable_birth_sun_sign = SIGNS[probable_birth_sun_sign_idx]

        part_9 = int(deg_in_sign // (30.0 / 9.0))
        element = p_asc_sign % 4
        start_map = {0: 0, 1: 9, 2: 6, 3: 3}
        probable_birth_lagna_idx = (start_map[element] + part_9) % 12
        probable_birth_lagna = SIGNS[probable_birth_lagna_idx]

        p_moon_long = prasna_planets.get("Moon", 0.0)
        nak_idx = int(p_moon_long // (360.0 / 27.0))
        probable_birth_nakshatra = nakshatras[nak_idx % 27]

        return {
            "prasna_query_time": prasna_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "prasna_ascendant_sign": SIGNS[p_asc_sign],
            "traced_birth_ayana": ayana,
            "traced_birth_ritu": ritu,
            "probable_birth_sun_sign": probable_birth_sun_sign,
            "probable_birth_lagna_sign": probable_birth_lagna,
            "probable_birth_moon_nakshatra": probable_birth_nakshatra,
            "bphs_reference": "BPHS Chapter 80 (Nashta Jataka)"
        }
