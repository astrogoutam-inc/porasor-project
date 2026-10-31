"""Vimshottari timing and Parashari transit-to-natal analysis.
All input longitudes are Lahiri sidereal degrees (0..360).
Dates are naive UTC datetimes at this module boundary.
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

DASHA = [("Ketu",7), ("Venus",20), ("Sun",6), ("Moon",10),
         ("Mars",7), ("Rahu",18), ("Jupiter",16), ("Saturn",19), ("Mercury",17)]
TOTAL = 120.0
YEAR_DAYS = 365.2425
NAKSHATRA_NAMES = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
"Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni",
"Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula",
"Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha",
"Purva Bhadrapada","Uttara Bhadrapada","Revati"]


def _add_years(dt: datetime, years: float) -> datetime:
    return dt + timedelta(days=years * YEAR_DAYS)


def _periods(start: datetime, years: float, first_lord: str, level: int=1) -> List[Dict[str, Any]]:
    idx = next(i for i,(p,_) in enumerate(DASHA) if p == first_lord)
    out=[]; cursor=start
    for j in range(9):
        lord, lord_years = DASHA[(idx+j)%9]
        span_years = years * lord_years / TOTAL
        end = _add_years(cursor, span_years)
        item={"lord":lord,"start_utc":cursor.isoformat()+"Z","end_utc":end.isoformat()+"Z","duration_years":round(span_years,6)}
        if level < 3:
            item["subperiods"] = _periods(cursor, span_years, lord, level+1)
        out.append(item); cursor=end
    return out


def vimshottari_timeline(moon_longitude: float, birth_utc: datetime, as_of_utc: datetime=None) -> Dict[str, Any]:
    lon=float(moon_longitude)%360.0
    nak_span=360.0/27.0
    nak_idx=min(26,int(lon/nak_span))
    frac=(lon-nak_idx*nak_span)/nak_span
    md_idx=nak_idx%9
    birth_lord, birth_years=DASHA[md_idx]
    balance=birth_years*(1.0-frac)
    elapsed=birth_years*frac
    first_start=birth_utc-timedelta(days=elapsed*YEAR_DAYS)
    cursor=birth_utc
    md_list=[]
    # first Mahadasha is clipped to birth; following eight + one cycle as needed
    sequence=[DASHA[(md_idx+i)%9] for i in range(9)]
    for cycle in range(3):
        for i,(lord,yrs) in enumerate(sequence):
            if cycle==0 and i==0:
                start=birth_utc; span=balance
            else:
                start=cursor; span=yrs
            end=_add_years(start,span)
            # antardashas in first partial MD begin at birth's antardasha position
            if cycle==0 and i==0:
                full_ads=_periods(first_start,birth_years,lord,2)
                ads=[]
                for ad in full_ads:
                    astart=datetime.fromisoformat(ad['start_utc'].replace('Z',''))
                    aend=datetime.fromisoformat(ad['end_utc'].replace('Z',''))
                    if aend>birth_utc:
                        clip_start=max(astart,birth_utc)
                        ad2=dict(ad); ad2['start_utc']=clip_start.isoformat()+'Z'
                        ad2['subperiods']=[x for x in ad.get('subperiods',[]) if datetime.fromisoformat(x['end_utc'].replace('Z',''))>birth_utc]
                        ads.append(ad2)
            else:
                ads=_periods(start,span,lord,2)
            md_list.append({"lord":lord,"start_utc":start.isoformat()+"Z","end_utc":end.isoformat()+"Z","duration_years":round(span,6),"antardashas":ads})
            cursor=end
        # next cycle follows the same 120-year sequence
    asof=as_of_utc or datetime.now(timezone.utc).replace(tzinfo=None)
    current={"mahadasha":None,"antardasha":None,"pratyantardasha":None,"start_utc":None,"end_utc":None}
    for md in md_list:
        ms=datetime.fromisoformat(md['start_utc'].replace('Z','')); me=datetime.fromisoformat(md['end_utc'].replace('Z',''))
        if ms<=asof<me:
            current['mahadasha']=md['lord']; current['start_utc']=md['start_utc']; current['end_utc']=md['end_utc']
            for ad in md['antardashas']:
                ads=datetime.fromisoformat(ad['start_utc'].replace('Z','')); ade=datetime.fromisoformat(ad['end_utc'].replace('Z',''))
                if ads<=asof<ade:
                    current['antardasha']=ad['lord']
                    current['antardasha_start_utc']=ad['start_utc']; current['antardasha_end_utc']=ad['end_utc']
                    for pd in ad.get('subperiods',[]):
                        pds=datetime.fromisoformat(pd['start_utc'].replace('Z','')); pde=datetime.fromisoformat(pd['end_utc'].replace('Z',''))
                        if pds<=asof<pde:
                            current['pratyantardasha']=pd['lord']
                            current['pratyantardasha_start_utc']=pd['start_utc']; current['pratyantardasha_end_utc']=pd['end_utc']
                            break
                    break
            break
    return {"system":"Vimshottari 120-year cycle","nakshatra":NAKSHATRA_NAMES[nak_idx],"nakshatra_index":nak_idx+1,"nakshatra_fraction_traversed":round(frac,8),"birth_mahadasha":birth_lord,"balance_at_birth_years":round(balance,6),"timeline":md_list,"current":current,"calculation_note":"Calendar durations use 365.2425 days per Vimshottari year; verify against chosen traditional software conventions for final publication."}


SIGNS=["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
ASPECT_HOUSES={"Mars":(4,7,8),"Jupiter":(5,7,9),"Saturn":(3,7,10)}

def _house_from_sign(planet_sign:int, target_sign:int)->int:
    return ((target_sign-planet_sign)%12)+1

def transit_to_natal(natal:Dict[str,float], transit:Dict[str,float], natal_asc:float, timestamp:str) -> Dict[str,Any]:
    asc_sign=int(float(natal_asc)//30)%12
    natal_signs={p:int(float(v)//30)%12 for p,v in natal.items()}
    transit_signs={p:int(float(v)//30)%12 for p,v in transit.items()}
    planet_rows=[]
    for tp,tdeg in transit.items():
        ts=transit_signs[tp]
        transit_house=_house_from_sign(asc_sign,ts)
        target_houses=list(ASPECT_HOUSES.get(tp,(7,)))
        for np,ndeg in natal.items():
            ns=natal_signs[np]
            rel=_house_from_sign(ts,ns)
            if rel in target_houses:
                diff=abs((float(tdeg)-float(ndeg)+180)%360-180)
                planet_rows.append({"transiting_planet":tp,"natal_planet":np,"transit_sign":SIGNS[ts],"natal_sign":SIGNS[ns],"transit_house_from_natal_lagna":transit_house,"parashari_aspect_house":rel,"exact_separation_degrees":round(diff,3),"aspect_rule":"7th aspect (all planets)" if rel==7 else f"{tp} special {rel}th aspect","interpretation_status":"geometric/aspect contact; judgement requires natal lordship, dignity and Dasha context"})
    house_rows=[]
    for p,deg in transit.items():
        s=int(float(deg)//30)%12
        house_rows.append({"planet":p,"sidereal_longitude":float(deg),"sign":SIGNS[s],"house_from_natal_lagna":_house_from_sign(asc_sign,s)})
    return {"timestamp_utc":timestamp,"natal_lagna_sign":SIGNS[asc_sign],"transiting_planets_in_natal_whole_sign_houses":house_rows,"parashari_transit_to_natal_planet_aspects":planet_rows,"aspect_method":"Whole-sign Parashari graha drishti: all planets 7th; Mars 4th/7th/8th; Jupiter 5th/7th/9th; Saturn 3rd/7th/10th. Rahu/Ketu special aspects are not assumed.","limitations":"This is a geometric transit contact layer, not a complete event prediction. Strength, house lordship, retrogression, combustion, divisional charts and running Dasha must be assessed before timing conclusions."}
