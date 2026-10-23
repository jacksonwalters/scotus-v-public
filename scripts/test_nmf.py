"""Compare 50/100/200-topic NMF retrieval on verified complete case sources."""
import argparse
from collections import Counter
import importlib.metadata
import json
from pathlib import Path
import resource
import sys
import time
import warnings
import joblib
import numpy as np
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from scvpublic.build import digest
from scvpublic.summary import source_texts
from scvpublic.topics import topic_coordinates,ranked_cases


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=Path('artifacts/nmf-evaluation'))
    p.add_argument('--artifact',type=Path,default=Path('artifacts/gss-bigram.sqlite'))
    p.add_argument('--solver',choices=['cd','mu'],default='mu')
    p.add_argument('--max-features',type=int,default=None)
    p.add_argument('--topics',type=int,nargs='+',default=[50,100,200])
    a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    docs,texts,origins=source_texts(a.artifact)
    a.output.mkdir(parents=True)
    vectorizer=TfidfVectorizer(ngram_range=(1,2),stop_words='english',min_df=3,
                              max_df=1.,max_features=a.max_features,sublinear_tf=True,dtype=np.float32)
    matrix=vectorizer.fit_transform(texts[d['case_id']] for d in docs)
    vocab=vectorizer.get_feature_names_out()
    labels=json.loads(Path('data/evaluation/court-relevance.json').read_text())['queries']
    queries=list(labels)+['contraception','civil rights','health care','zzzznomatchzzzz']
    query_matrix=vectorizer.transform(queries)
    joblib.dump(vectorizer,a.output/'vectorizer.joblib')
    (a.output/'documents.json').write_text(json.dumps(docs)+'\n')
    report=dict(artifact_sha256=digest(a.artifact),source_counts=dict(Counter(origins.values())),
                documents=len(docs),features=len(vocab),nonzeros=matrix.nnz,
                vectorizer=vectorizer.get_params(),versions={k:importlib.metadata.version(k) for k in ['numpy','scipy','scikit-learn']},models={})
    report['vectorizer']['dtype']='float32'
    def evaluate(scores,q):
        hits=ranked_cases(scores,docs);ids=[h['case_id'] for h in hits]
        result=dict(top10=hits[:10],above_20_percent=sum(h['score']>=hits[0]['score']*.2 for h in hits) if hits else 0)
        if q in labels:
            result['relevant_ranks']={i:ids.index(i)+1 if i in ids else None for i in labels[q]['relevant']}
            result['known_relevant_top10']=sum(i in ids[:10] for i in labels[q]['relevant'])
            result['known_irrelevant_top10']=sum(i in ids[:10] for i in labels[q]['irrelevant'])
        return result
    report['same_matrix_tfidf']={q:evaluate((matrix@query_matrix[j].T).toarray().ravel(),q) for j,q in enumerate(queries)}
    print(f'{matrix.shape} matrix, {matrix.nnz} entries',flush=True)
    for count in a.topics:
        start=time.monotonic()
        model=NMF(n_components=count,solver=a.solver,init='nndsvda',random_state=42,max_iter=300,tol=1e-4)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            weights=model.fit_transform(matrix)
        fit_seconds=time.monotonic()-start
        cases=topic_coordinates(weights,model.components_)
        start=time.monotonic()
        with warnings.catch_warnings(record=True) as query_warnings:
            warnings.simplefilter('always')
            query_weights=model.transform(query_matrix)
        query_seconds=time.monotonic()-start
        qcoords=topic_coordinates(query_weights,model.components_)
        results={}
        for j,q in enumerate(queries):
            result=evaluate(cases@qcoords[j],q)
            result['matched_features']=[str(vocab[i]) for i in query_matrix[j].indices]
            result['topics']=[dict(id=int(t),weight=float(qcoords[j,t]),terms=[str(vocab[i]) for i in np.argsort(-model.components_[t])[:15]],
                                   examples=[docs[int(i)]['name'] for i in np.argsort(-cases[:,t])[:5]])
                              for t in np.argsort(-qcoords[j])[:3] if qcoords[j,t]>0]
            results[q]=result
        folder=a.output/str(count);folder.mkdir()
        joblib.dump(model,folder/'model.joblib')
        np.save(folder/'case_topics.npy',cases)
        stats=dict(solver=a.solver,fit_seconds=fit_seconds,query_batch_seconds=query_seconds,iterations=model.n_iter_,
                   warnings=[str(w.message) for w in caught+query_warnings],queries=results,
                   matrix_bytes=model.components_.nbytes+cases.nbytes)
        report['models'][str(count)]=stats
        (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(count,round(fit_seconds,2),'seconds',model.n_iter_,'iterations',stats['warnings'],flush=True)
        for q in labels:print(q,results[q]['known_relevant_top10'],results[q]['known_irrelevant_top10'],results[q]['relevant_ranks'],flush=True)
    report['peak_training_rss_mib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1024**2 if sys.platform=='darwin' else 1024)
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
