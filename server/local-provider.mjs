// Local desktop adapter: use Python's verified TLS trust store when Node cannot connect.
import {spawn} from 'node:child_process';
export async function localProviderFetch(url,options={}){
 if(!url.startsWith('https://api.deepseek.com/'))throw new Error('Unexpected provider destination');
 const python=process.env.RAG_PYTHON||'python3';
 const code=`import sys,json,urllib.request,urllib.error,os
p=json.load(sys.stdin)
r=urllib.request.Request(p['url'],data=p['body'].encode(),headers={'Authorization':'Bearer '+os.environ['DEEPSEEK_API_KEY'],'Content-Type':'application/json'})
try:
 with urllib.request.urlopen(r,timeout=60) as response: print(json.dumps({'status':response.status,'body':response.read().decode()}))
except urllib.error.HTTPError as e: print(json.dumps({'status':e.code,'body':'{}'}))
`;
 const result=await new Promise((resolve,reject)=>{const p=spawn(python,['-c',code],{stdio:['pipe','pipe','pipe']});let data='';p.stdout.on('data',b=>data+=b);p.stderr.resume();p.on('error',reject);p.on('close',n=>n?reject(new Error('Provider connection failed')):resolve(data));const onAbort=()=>p.kill();options.signal?.addEventListener('abort',onAbort,{once:true});p.on('close',()=>options.signal?.removeEventListener('abort',onAbort));p.stdin.end(JSON.stringify({url,body:options.body}));});
 const parsed=JSON.parse(result);return new Response(parsed.body,{status:parsed.status,headers:{'Content-Type':'application/json'}});
}
