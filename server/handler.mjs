import {answerQuestion,PRODUCT_MODELS} from './rag.mjs';
const json=(body,status=200)=>new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});
export function createHandler(index,assets,providerFetch=fetch){
 let inFlight=0;let started=[];
 return async function handle(request,env){
  const url=new URL(request.url);
  try{
   if(url.pathname==='/api/catalog'&&request.method==='GET')return json({documents:index.documents.map(({model,filename,pages})=>({model,filename,pages})),pages:index.documents.reduce((n,d)=>n+d.pages,0),chunks:index.chunks.length,mode:'grounded',ready:!!env.DEEPSEEK_API_KEY});
   if(url.pathname==='/api/document'&&request.method==='GET'){
    const model=url.searchParams.get('model');if(!PRODUCT_MODELS.includes(model))return json({error:'型号不存在'},404);
    const page=Number(url.searchParams.get('page')||0);const selected=index.chunks.filter(c=>c.model===model&&(!page||c.page===page)).slice(0,page?4:2);
    return json({document:index.documents.find(d=>d.model===model),excerpts:selected.map(({id,page,text,section})=>({id,page,text,section}))});
   }
   if(url.pathname==='/api/chat'){
    if(request.method!=='POST')return json({error:'Method not allowed'},405);
    const origin=request.headers.get('origin');if(origin&&origin!==url.origin)return json({error:'请在已登录的知识库页面提问'},403);
    if(!request.headers.get('content-type')?.includes('application/json'))return json({error:'请输入有效问题'},415);
    if(Number(request.headers.get('content-length')||0)>12000)return json({error:'问题过长'},413);
    const raw=await request.text();if(raw.length>12000)return json({error:'问题过长'},413);
    let body;try{body=JSON.parse(raw)}catch{return json({error:'请求格式错误'},400)}
    if(typeof body.question!=='string'||!body.question.trim()||body.question.length>1500)return json({error:'问题长度需在 1—1500 字之间'},400);
    if(body.model&&body.model!=='auto'&&!PRODUCT_MODELS.includes(body.model))return json({error:'型号不存在'},400);
    if(!env.DEEPSEEK_API_KEY)return json({error:'模型服务尚未配置，未生成模拟回答'},503);
    // Owner-only platform access is the primary authorization boundary. This is an additional burst limit, not a global quota.
    started=started.filter(t=>Date.now()-t<60000);if(inFlight>=2||started.length>=12)return json({error:'提问较频繁，请稍后重试'},429);
    inFlight++;started.push(Date.now());try{return json(await answerQuestion(index,body,env,providerFetch))}finally{inFlight--}
   }
   if(url.pathname.startsWith('/api/'))return json({error:'Not found'},404);
   if(request.method!=='GET'&&request.method!=='HEAD')return new Response('Method not allowed',{status:405});
   const path=url.pathname==='/'?'/index.html':url.pathname;const asset=assets[path];
   if(!asset)return new Response('Not found',{status:404});
   return new Response(request.method==='HEAD'?null:asset.body,{headers:{'Content-Type':asset.type,'Cache-Control':'no-cache','X-Content-Type-Options':'nosniff','Referrer-Policy':'same-origin','Content-Security-Policy':"default-src 'self'; script-src 'self' blob: 'wasm-unsafe-eval' https://cdn.jsdelivr.net; style-src 'self'; img-src 'self' data:; connect-src 'self' https://cdn.jsdelivr.net https://huggingface.co https://*.huggingface.co https://*.hf.co; worker-src 'self' blob:; base-uri 'none'; object-src 'none'; form-action 'self'"}});
  }catch(error){return json({error:typeof error.message==='string'?error.message:'服务暂时不可用，请重试'},502)}
 };
}
