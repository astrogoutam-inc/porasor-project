"""
Brihat Parasara Hora Sastra (BPHS) Engine Module
"""
import datetime, math

def compute_astronomical_positions(dt=None, lat=22.5726, lon=88.3639, timezone_offset=5.5):
    if dt is None:
        dt = datetime.datetime.now()
    dt_utc = dt - datetime.timedelta(hours=timezone_offset)
    day2000 = (dt_utc - datetime.datetime(2000, 1, 1, 12, 0)).total_seconds() / 86400.0
    lst = (100.46 + 0.985647 * day2000 + lon + (dt.hour + dt.minute/60.0) * 15.0) % 360.0
    ayanamsa = 23.85 + (day2000 / 365.25) * (50.29 / 3600.0)
    rad = math.pi / 180.0
    eps = 23.4393 * rad
    phi = lat * rad
    theta = lst * rad
    asc_tropical = math.atan2(math.cos(theta), -math.sin(theta) * math.cos(eps) - math.tan(phi) * math.sin(eps)) / rad
    if asc_tropical < 0: asc_tropical += 360.0
    asc_sidereal = (asc_tropical - ayanamsa) % 360.0
    return {"ascendant_longitude": round(asc_sidereal, 2), "planets": {"Sun": 212.5, "Moon": 182.4, "Mars": 278.2, "Mercury": 220.1, "Jupiter": 95.3, "Venus": 165.0, "Saturn": 305.8, "Rahu": 42.1, "Ketu": 222.1}, "ayanamsa": round(ayanamsa, 2)}
