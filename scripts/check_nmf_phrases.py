"""Check exact-phrase query projection without changing the fitted topics."""
import argparse,json
from pathlib import Path
import joblib
import numpy as np
from scvpublic.topics import topic_coordinates,ranked_cases


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);a=p.parse_args()
 vectorizer=joblib.load(a.bundle/'vectorizer.joblib')
 docs=json.loads((a.bundle/'documents.json').read_text())
 labels=json.loads(Path('data/evaluation/court-relevance.json').read_text())['queries']
 queries=list(labels)+['contraception','civil rights','health care','zzzznomatchzzzz']
 x=vectorizer.transform(queries).tolil()
 modes={}
 for j,q in enumerate(queries):
  if ' ' in q and q in vectorizer.vocabulary_:
   x.rows[j]=[vectorizer.vocabulary_[q]];x.data[j]=[1.];modes[q]='whole phrase'
  else:modes[q]='original features'
 x=x.tocsr();report={}
 for folder in sorted(a.bundle.iterdir()):
  if not (folder/'model.joblib').is_file():continue
  model=joblib.load(folder/'model.joblib');cases=np.load(folder/'case_topics.npy',mmap_mode='r')
  coords=topic_coordinates(model.transform(x),model.components_);results={}
  for j,q in enumerate(queries):
   hits=ranked_cases(cases@coords[j],docs);ids=[h['case_id'] for h in hits]
   results[q]=dict(projection=modes[q],top10=hits[:10])
   if q in labels:
    results[q].update(relevant_ranks={i:ids.index(i)+1 if i in ids else None for i in labels[q]['relevant']},
                     known_relevant_top10=sum(i in ids[:10] for i in labels[q]['relevant']),
                     known_irrelevant_top10=sum(i in ids[:10] for i in labels[q]['irrelevant']))
    print(folder.name,q,results[q]['relevant_ranks'],flush=True)
  report[folder.name]=results
 (a.bundle/'phrase-query-report.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
