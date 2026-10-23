"""Evaluate the phrase expansion candidate without treating unjudged cases as irrelevant."""
import argparse,json,resource,sys,time
from pathlib import Path
from scvpublic.expansion import ExpandedSearch
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--bundle',default='artifacts/query-expansion')
p.add_argument('--output',default='artifacts/expansion-evaluation.json')
a=p.parse_args();engine=ExpandedSearch(a.bundle)
labels=json.loads(Path('data/evaluation/court-relevance.json').read_text())['queries'];result={}
for q in [*labels,'contraception','civil rights','health care','zzzznomatchzzzz']:
 t=time.monotonic();hits,expanded=engine.search([q]);ids=[h['case_id'] for h in hits]
 result[q]=dict(seconds=time.monotonic()-t,expansions=expanded,hits=hits)
 if q in labels:
  result[q]['judgments']=dict(relevant_ranks={i:ids.index(i)+1 if i in ids else None for i in labels[q]['relevant']},irrelevant_retained=[i for i in labels[q]['irrelevant'] if i in ids])
 print(q,len(hits),expanded,result[q].get('judgments',''),flush=True)
report=dict(queries=result,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1024**2 if sys.platform=='darwin' else 1024))
Path(a.output).write_text(json.dumps(report,indent=2)+'\n');print('Peak RSS',report['peak_rss_mib'])
