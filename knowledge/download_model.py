"""Download pinned local embedding weights from the model publisher (no API key)."""
import argparse,concurrent.futures,urllib.request
from pathlib import Path
MODEL='Xenova/paraphrase-multilingual-MiniLM-L12-v2'
REVISION='2c4055b12046f11709e9df2c122e59ffbdc2f900'
p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=Path.home()/'.cache/chuangan-embedding');a=p.parse_args()
root=a.cache/MODEL
files=['config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json','onnx/model_quantized.onnx']
def download(name):
 path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
 if not path.exists():
  temporary=path.with_suffix(path.suffix+'.part')
  with urllib.request.urlopen(f'https://huggingface.co/{MODEL}/resolve/{REVISION}/{name}',timeout=120) as response,temporary.open('wb') as output:
   while True:
    chunk=response.read(1024*1024)
    if not chunk:break
    output.write(chunk)
  temporary.replace(path)
 print(name,path.stat().st_size,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(download,files))
