"""Conservative concept expansion followed by phrase-filtered summary TF-IDF."""
from contextlib import closing
from functools import lru_cache
import json
from pathlib import Path
import re
import threading
from .build import digest
from .encoding import Encoder
from .store import connect, search


def normalize(text):
    return ' '.join(re.findall(r'\w+', text.lower()))


def phrase_matches(db, expression):
    expression=normalize(expression)
    if not expression:return set()
    return {r[0] for r in db.execute('SELECT rowid FROM court_phrases WHERE court_phrases MATCH ?', ('"'+expression+'"',))}


class ExpandedSearch:
    def __init__(self, folder):
        import numpy as np
        self.folder=Path(folder)
        manifest=json.loads((self.folder/'manifest.json').read_text())
        for name,checksum in manifest['files'].items():
            if digest(self.folder/name)!=checksum:raise ValueError('Expansion checksum mismatch: '+name)
        self.encoder=Encoder(folder)
        self.vectors=np.load(self.folder/'vectors.npy',mmap_mode='r',allow_pickle=False)
        self.terms=json.loads((self.folder/'terms.json').read_text())
        if self.vectors.shape!=(len(self.terms),384):raise ValueError('Vocabulary mismatch')
        self.artifact=self.folder/'search.sqlite'
        self.lock=threading.Lock()

    def search(self, terms):
        with self.lock:
            hits,expanded=self._search(tuple(normalize(t) for t in terms if normalize(t)))
            return list(hits),list(expanded)

    @lru_cache(maxsize=32)
    def _search(self, terms):
        import numpy as np
        if not terms:return (),()
        hits={}; expansions=[]
        with closing(connect(self.artifact)) as db:
            documents={i:json.loads(p) for i,p in db.execute("SELECT id,payload FROM documents WHERE corpus='court'")}
            by_case={d['case_id']:i for i,d in documents.items()}
            for query in terms:
                similarity=self.vectors@self.encoder.encode([query])[0]
                alternatives=[self.terms[int(i)] for i in np.argsort(-similarity,kind='stable')
                              if similarity[i]>=.78 and self.terms[int(i)]!=query][:3]
                expansions.append(dict(query=query,alternatives=alternatives))
                for expression,weight in [(query,1.)]+[(term,.5) for term in alternatives]:
                    # Conservative surface variants; exact multiword phrase remains intact.
                    variants=[expression,expression+'s']
                    eligible=set();scores={}
                    for variant in variants:
                        eligible.update(phrase_matches(db,variant))
                        for hit in search(db,'court',[variant],limit=None):
                            i=by_case[hit['case_id']]
                            scores[i]=max(scores.get(i,0.),hit['score'])
                    for i in eligible:
                        value=weight*scores.get(i,0.)
                        if value>hits.get(i,0.):hits[i]=value
            result=[dict(documents[i],score=value) for i,value in hits.items() if value>0]
        result.sort(key=lambda h:(-h['score'],h['case_id']))
        return tuple(result),tuple(expansions)
