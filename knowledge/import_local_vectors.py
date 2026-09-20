"""Replace SQLite vectors with locally generated embeddings and update the manifest."""
import argparse,json,sqlite3
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--data-dir',type=Path,required=True);a=p.parse_args();d=a.data_dir
corpus=json.loads((d/'knowledge-local.json').read_text());db=sqlite3.connect(d/'knowledge.sqlite')
for c in corpus['chunks']:
 v=np.array(c['vector'],dtype=np.float32)
 if v.shape!=(384,) or not np.isfinite(v).all():raise ValueError('Invalid local embedding')
 db.execute('UPDATE chunks SET vector=?,embedding_model=? WHERE id=?',(v.tobytes(),corpus['embedding_model'],c['id']))
db.commit();db.close()
m=json.loads((d/'index-manifest.json').read_text());m.update(embedding_model=corpus['embedding_model'],dimensions=384,embedded_chunks=len(corpus['chunks']),status='ready',embedding_runtime='local ONNX, q8');m.pop('embedding_tokens_this_run',None)
(d/'index-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));print('SQLite updated with local vectors:',len(corpus['chunks']))
