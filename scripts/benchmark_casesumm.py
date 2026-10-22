import pyarrow as pa, numpy as np, json,time,resource
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import save_npz
root=Path('data/raw/casesumm'); texts={}
for p in root.glob('*.arrow'):
 with pa.memory_map(str(p),'r') as f:
  for batch in pa.ipc.open_stream(f):
   for r in batch.to_pylist():
    s=r['opinion'] or ''
    if len(s.split())>=100 and len(s)>len(texts.get(r['citation'],'')):texts[r['citation']]=s
start=time.monotonic()
v=TfidfVectorizer(stop_words='english',min_df=.00001,max_df=.30,dtype=np.float32)
x=v.fit_transform(texts.values())
out=root/'benchmark-tfidf.npz';save_npz(out,x)
report=dict(documents=x.shape[0],terms=x.shape[1],nonzeros=x.nnz,csr_bytes=x.data.nbytes+x.indices.nbytes+x.indptr.nbytes,npz_bytes=out.stat().st_size,build_save_seconds=round(time.monotonic()-start,2),peak_process_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
(root/'benchmark.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
