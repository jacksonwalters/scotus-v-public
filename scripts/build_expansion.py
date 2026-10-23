"""Build a phrase-aware summary index and a compact concept embedding vocabulary."""
import argparse
import json
from pathlib import Path
import re
import shutil
import sqlite3
import zipfile
import numpy as np
from scvpublic.build import digest
from scvpublic.summary import source_texts
from scvpublic.encoding import Encoder


def normalize(text): return ' '.join(re.findall(r'\w+',text.lower()))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('artifacts/query-expansion'))
    parser.add_argument('--dictionary',type=Path,default=Path('data/raw/wordnet.zip'))
    args=parser.parse_args()
    output=args.output
    if output.exists():raise FileExistsError(output)
    source=args.dictionary
    spec=json.loads(Path('data/manifests/wordnet.json').read_text())
    if digest(source)!=spec['sha256']:raise ValueError('Dictionary checksum mismatch')
    docs,texts,origins=source_texts('artifacts/gss-bigram.sqlite')
    vocabulary=set()
    with zipfile.ZipFile(source) as archive:
        for file in ['data.noun','data.adj','data.verb']:
            for line in archive.read('wordnet/'+file).decode().splitlines():
                if line.startswith(' '):continue
                fields=line.split('|')[0].split()
                vocabulary.update(normalize(fields[4+2*i].replace('_',' ')) for i in range(int(fields[3],16)))
        license_text=archive.read('wordnet/LICENSE').decode()
    present=set()
    plural_map={term+'s':term for term in vocabulary}
    for text in texts.values():
        words=normalize(text).split()
        for length in range(1,5):
            for i in range(len(words)-length+1):
                phrase=' '.join(words[i:i+length])
                if phrase in vocabulary:present.add(phrase)
                if phrase in plural_map:present.add(plural_map[phrase])
    terms=sorted(present)
    output.mkdir()
    shutil.copyfile('artifacts/gss-summary.sqlite',output/'search.sqlite')
    with sqlite3.connect(output/'search.sqlite') as db:
        db.execute("CREATE VIRTUAL TABLE court_phrases USING fts5(text, tokenize='unicode61')")
        db.executemany('INSERT INTO court_phrases(rowid,text) VALUES (?,?)',((d['doc_id'],texts[d['case_id']]) for d in docs))
    model_spec=json.loads(Path('data/manifests/semantic-model.json').read_text())
    for name,checksum in model_spec['files'].items():
        if digest(Path('artifacts/semantic-model')/name)!=checksum:
            raise ValueError('Query model checksum mismatch: '+name)
    encoder=Encoder('artifacts/semantic-model')
    vectors=[]
    for start in range(0,len(terms),64):
        vectors.append(encoder.encode(terms[start:start+64]))
        if start%2048==0:print(start,len(terms),flush=True)
    np.save(output/'vectors.npy',np.concatenate(vectors))
    (output/'terms.json').write_text(json.dumps(terms)+'\n')
    (output/'WORDNET-LICENSE').write_text(license_text)
    for name in ['model.onnx','tokenizer.json']:
        shutil.copyfile(Path('artifacts/semantic-model')/name,output/name)
    manifest=dict(description='Dictionary-constrained semantic query expansion; full summary phrase matches',
        dictionary_url='https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/wordnet.zip',
        dictionary_sha256=digest(source),base_sha256=digest('artifacts/gss-summary.sqlite'),
        model=json.loads(Path('data/manifests/semantic-model.json').read_text()),terms=len(terms),
        files={p.name:digest(p) for p in output.iterdir() if p.is_file()})
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Complete',len(terms),flush=True)

if __name__=='__main__':main()
