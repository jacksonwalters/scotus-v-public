"""Offline CaseSumm inspection; pip install pyarrow==19.0.1 first."""
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import pyarrow as pa

root=Path('data/raw/casesumm')
def key(s):
    m=re.fullmatch(r'\s*(\d+)\s*\.?\s*U\.?\s*S\.?\s*(\d+)\s*',s,re.I)
    return f'{int(m[1])} U.S. {int(m[2])}' if m else None
scdb=defaultdict(list)
all_scdb=[]
dockets=defaultdict(list)
for file in Path('data/scdb').glob('*.csv'):
    with file.open(encoding='cp1252') as f:
        for row in csv.DictReader(f):
            all_scdb.append(row)
            dockets[(row['term'],row['docket'])].append(row)
            k=key(row['usCite'])
            if k:scdb[k].append(row)
seen=Counter(); lengths=[]; examples={}; hashes=Counter(); valid=set(); schema=None
empty=[]; short=[]; malformed=[]; matched=set(); matched_ids=set(); docket_hits=0
for file in sorted(root.glob('*.arrow')):
    with pa.memory_map(str(file),'r') as source:
        reader=pa.ipc.open_stream(source);schema=str(reader.schema)
        for batch in reader:
            for row in batch.to_pylist():
                k=key(row['citation']);text=row['opinion'] or '';n=len(text.split())
                seen[row['citation']]+=1;lengths.append(n);hashes[hashlib.sha256(text.encode()).hexdigest()]+=1
                if not k:malformed.append(row['citation'])
                if n==0:empty.append(k)
                if n<100:short.append(k)
                if k in scdb:
                    matched_ids.update(r['caseId'] for r in scdb[k])
                    matched.add(k)
                    if n>=100:valid.add(k)
                special=re.fullmatch(r'\d+\.US\.(\d{4})_(.+)',row['citation'])
                if special:
                    candidates=dockets.get((special[1],special[2]),[])
                    if len({r['caseId'] for r in candidates})==1:
                        matched_ids.add(candidates[0]['caseId']); docket_hits+=1
                if k in ['410 U.S. 113','505 U.S. 833','576 U.S. 644','554 U.S. 570','347 U.S. 483']:
                    examples[k]={'words':n,'opening':text[:600],'ending':text[-400:]}
lengths.sort()
coverage={}
for lo,hi in [(1948,2016),(1950,2016),(1950,2019)]:
    keys={k for k,rows in scdb.items() if any(lo<=int(r['dateDecision'].split('/')[-1])<=hi for r in rows)}
    coverage[f'{lo}-{hi}']=dict(scdb_distinct_citations=len(keys),matched=len(keys&matched),matched_100_words=len(keys&valid),missing=len(keys-matched))
byyear=defaultdict(lambda:Counter())
for k,rows in scdb.items():
    for year in {int(r['dateDecision'].split('/')[-1]) for r in rows}:
        byyear[year]['scdb_citations']+=1
        if k in matched:byyear[year]['matched']+=1
        if k in valid:byyear[year]['matched_100_words']+=1
with (root/'coverage_by_year.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['year','scdb_citations','matched','matched_100_words'])
    for y,c in sorted(byyear.items()):w.writerow([y,c['scdb_citations'],c['matched'],c['matched_100_words']])
full_ids={r['caseId'] for r in all_scdb if 1950<=int(r['dateDecision'].split('/')[-1])<=2016}
report=dict(full_scdb_1950_2016_cases=len(full_ids),matched_cases_citation_or_unique_term_docket=len(full_ids & matched_ids),unique_term_docket_rows=docket_hits,revision='880acec67a69766075ddb42882de4722efdeddb2',schema=schema,rows=len(lengths),unique_citations=len(seen),duplicate_citation_rows=sum(n-1 for n in seen.values()),empty=len(empty),under_100_words=len(short),malformed_citations=malformed,word_quantiles={str(p):lengths[int((len(lengths)-1)*p)] for p in [0,.1,.5,.9,1]},duplicate_text_rows=sum(n-1 for n in hashes.values()),coverage=coverage,examples=examples,files={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()) for p in root.glob('*.arrow')})
(root/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['malformed_citations','examples']},indent=2))
