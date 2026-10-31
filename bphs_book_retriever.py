"""Simple local, page-traceable lexical retrieval over the supplied BPHS PDF text."""
from pathlib import Path
import re
from typing import List, Dict, Any

STOP=set("the and for with from that this your are was were into about according based what when will can could should have has had does did how why my me our their them then than also only not but you his her its its an a of to in on at by as is be or if it we they i".split())
class BPHSBookRetriever:
    def __init__(self, text_path=None):
        self.path=Path(text_path) if text_path else Path(__file__).resolve().parent/'references'/'bphs_book.txt'
        self.pages=[]
        if self.path.exists():
            raw=self.path.read_text(encoding='utf-8',errors='ignore')
            self.pages=[p.strip() for p in raw.split('\f') if p.strip()]
    def search(self, query:str, limit:int=5)->List[Dict[str,Any]]:
        if not self.pages:return []
        terms=[t for t in re.findall(r'[a-zA-Z]{3,}|[\u0980-\u09FF]{2,}',query.lower()) if t not in STOP]
        expansions={
          "অর্থ":["wealth","money","dhan","finance","income","gain","labh","dhan bhava"],
          "আর্থিক":["wealth","money","finance","income","gain"],
          "চাকরি":["profession","career","karma","tenth house","employment"],
          "কর্মজীবন":["profession","career","karma bhava","tenth house"],
          "ব্যবসা":["business","trade","profession","income"],
          "বিবাহ":["marriage","wife","husband","seventh house","yuvati"],
          "বিয়ে":["marriage","seventh house","yuvati"],
          "সন্তান":["children","progeny","putra","fifth house"],
          "বিদেশ":["foreign","travel","twelfth house","ninth house"],
          "সম্পত্তি":["property","fourth house","bandhu bhava"],
          "দশা":["dasha","vimshottari","mahadasha","antardasha"],
          "গোচর":["transit","gochara","saturn","jupiter"],
          "আয়ু":["longevity","life span","eighth house","maraka"]
        }
        expanded=list(terms)
        for bn,words in expansions.items():
            if bn in query:
                expanded.extend(words)
        terms=list(dict.fromkeys(expanded))
        if not terms:return []
        scored=[]
        for i,page in enumerate(self.pages,1):
            low=page.lower(); score=sum(low.count(t) for t in terms)
            if score:
                # keep compact excerpts around first query hit
                hit=min([low.find(t) for t in terms if low.find(t)>=0],default=0)
                start=max(0,hit-450); excerpt=page[start:start+1400].strip()
                scored.append((score,i,excerpt))
        scored.sort(key=lambda x:(-x[0],x[1]))
        return [{"page":i,"score":score,"excerpt":excerpt} for score,i,excerpt in scored[:limit]]
