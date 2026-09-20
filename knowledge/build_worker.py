"""Package a private Worker. Never publish the generated bundle or corpus to public GitHub."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--data-dir',type=Path,required=True);p.add_argument('--site-dir',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];site=a.site_dir
corpus=json.loads((a.data_dir/'knowledge-local.json').read_text())
for c in corpus['chunks']:c['vector']=[round(float(v),6) for v in c['vector']]
assets={}
for n,t in [('index.html','text/html; charset=utf-8'),('app.js','text/javascript; charset=utf-8'),('styles.css','text/css; charset=utf-8')]:assets['/'+n]={'body':(root/n).read_text(),'type':t}
core=(root/'server/rag.mjs').read_text().replace('export ','')
handler='\n'.join((root/'server/handler.mjs').read_text().splitlines()[1:]).replace('export ','')
content=core+'\n'+handler+'\nconst privateCorpus='+json.dumps(corpus,ensure_ascii=False,separators=(',',':'))+';\nconst privateAssets='+json.dumps(assets,ensure_ascii=False,separators=(',',':'))+';\nconst handle=createHandler(createIndex(privateCorpus),privateAssets);\nexport default { fetch(request,env){return handle(request,env);} };\n'
(site/'dist/server').mkdir(parents=True,exist_ok=True);(site/'dist/server/index.js').write_text(content)
(site/'dist/.openai').mkdir(parents=True,exist_ok=True)
manifest=json.loads((site/'.openai/hosting.json').read_text());manifest.pop('static',None)
(site/'.openai/hosting.json').write_text(json.dumps(manifest,indent=2))
(site/'dist/.openai/hosting.json').write_text(json.dumps(manifest,indent=2))
print('Private worker bundle bytes:',len(content.encode()))
