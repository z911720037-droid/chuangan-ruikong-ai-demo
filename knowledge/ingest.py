"""Build a local, page-cited SQLite vector index. Source PDF files are never copied to Git."""
import argparse, hashlib, json, re, sqlite3
from pathlib import Path
import numpy as np
from pypdf import PdfReader

EMBED_MODEL = 'Xenova/paraphrase-multilingual-MiniLM-L12-v2'
DIMENSIONS = 384
MODELS = ('CA100', 'CA700', '600U', 'CL100', 'CL200')

def chunks(text, limit=1200, overlap=200):
    text = re.sub(r'[\t \u3000]+', ' ', text).strip()
    if len(text) < 60: return []
    result=[]; start=0
    while start < len(text):
        end=min(start+limit,len(text))
        if end<len(text):
            boundary=text.rfind('\n',start+limit//2,end)
            if boundary>start: end=boundary
        part=text[start:end].strip()
        if len(part)>=60: result.append(part)
        if end==len(text): break
        start=max(start+1,end-overlap)
    return result

def build(source, output, embed):
    output.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(output/'knowledge.sqlite')
    db.execute('CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, filename TEXT, sha256 TEXT, pages INTEGER)')
    db.execute('CREATE TABLE IF NOT EXISTS chunks (id TEXT PRIMARY KEY, model TEXT, page INTEGER, text TEXT, hash TEXT, vector BLOB, embedding_model TEXT)')
    stats=[]; active_docs=[]; active_chunks=[]
    for file in sorted(source.glob('*.pdf')):
        model=next((m for m in MODELS if m in file.name.upper()),None)
        if not model: raise ValueError('Unrecognized model: '+file.name)
        if model in active_docs: raise ValueError('Multiple source PDFs for model '+model)
        active_docs.append(model)
        raw=file.read_bytes(); reader=PdfReader(file); short=[]; added=0
        db.execute('INSERT OR REPLACE INTO documents VALUES (?,?,?,?)',(model,file.name,hashlib.sha256(raw).hexdigest(),len(reader.pages)))
        for page_no,page in enumerate(reader.pages,1):
            text=page.extract_text() or ''
            if len(text.strip())<60: short.append(page_no)
            for index,text in enumerate(chunks(text)):
                cid=f'{model}-p{page_no:03d}-{index:02d}'
                digest=hashlib.sha256(text.encode()).hexdigest(); active_chunks.append(cid)
                previous=db.execute('SELECT hash,embedding_model FROM chunks WHERE id=?',(cid,)).fetchone()
                if not previous or previous!=(digest,EMBED_MODEL):
                    db.execute('INSERT OR REPLACE INTO chunks VALUES (?,?,?,?,?,NULL,?)',(cid,model,page_no,text,digest,EMBED_MODEL))
                added+=1
        stats.append({'model':model,'filename':file.name,'pdf_pages':len(reader.pages),'chunks':added,'short_text_pages':short,'sha256':hashlib.sha256(raw).hexdigest()})
    # Remove stale chunks if source content was shortened or replaced.
    db.execute('CREATE TEMP TABLE current_ids(id TEXT PRIMARY KEY)')
    db.executemany('INSERT INTO current_ids VALUES (?)',[(x,) for x in active_chunks])
    db.execute('DELETE FROM chunks WHERE id NOT IN (SELECT id FROM current_ids)')
    db.execute('DELETE FROM documents WHERE id NOT IN (SELECT DISTINCT model FROM chunks)')
    db.commit()
    usage=0
    total=db.execute('SELECT COUNT(*) FROM chunks').fetchone()[0]
    embedded=db.execute('SELECT COUNT(*) FROM chunks WHERE vector IS NOT NULL').fetchone()[0]
    manifest={'documents':stats,'total_pdf_pages':sum(d['pdf_pages'] for d in stats),'chunks':total,'embedded_chunks':embedded,'embedding_model':EMBED_MODEL,'dimensions':DIMENSIONS,'embedding_tokens_this_run':usage,'status':'ready' if total and embedded==total else 'not_embedded','page_numbering':'Physical PDF page number, 1-based; printed page numbers may differ.'}
    (output/'index-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    db.close();print(json.dumps({k:v for k,v in manifest.items() if k!='documents'},ensure_ascii=False),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    build(a.source,a.output,False)
