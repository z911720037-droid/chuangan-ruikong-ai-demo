import fs from 'node:fs';import {localEmbed,LOCAL_MODEL} from './local-embedding.mjs';
const dir=process.env.RAG_DATA_DIR;if(!dir)throw new Error('RAG_DATA_DIR required');
const corpus=JSON.parse(fs.readFileSync(dir+'/knowledge.json','utf8'));
for(let i=0;i<corpus.chunks.length;i++){
 const c=corpus.chunks[i];c.vector=await localEmbed(c.model+' 用户手册 PDF第'+c.page+'页\n'+c.text);
 if(i%25===0)console.log(JSON.stringify({embedded:i+1,total:corpus.chunks.length}));
}
corpus.embedding_model=LOCAL_MODEL;corpus.dimensions=384;
fs.writeFileSync(dir+'/knowledge-local.json',JSON.stringify(corpus));console.log('Local embeddings ready');
