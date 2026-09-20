"""Export SQLite vectors for the server build; keep output outside the public repository."""
import sqlite3,json,argparse
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--data-dir',type=Path,required=True);a=p.parse_args()
db=sqlite3.connect(a.data_dir/'knowledge.sqlite')
rows=db.execute('SELECT id,model,page,text,vector FROM chunks ORDER BY id').fetchall()
docs=[dict(zip(('model','filename','sha256','pages'),r)) for r in db.execute('SELECT * FROM documents ORDER BY id')]
data={'documents':docs,'chunks':[{'id':r[0],'model':r[1],'page':r[2],'text':r[3],'vector':np.frombuffer(r[4],dtype=np.float32).round(6).tolist() if r[4] else []} for r in rows]}
for c in data['chunks']:
    c['section'] = ('5.2.1 回馈部分' if c['page'] in (24,25) else '5.2.2 逆变部分' if 26 <= c['page'] <= 28 else '') if c['model']=='CL200' else ''
(a.data_dir/'knowledge.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
print('Exported',len(rows),'chunks,',len(docs),'documents')
