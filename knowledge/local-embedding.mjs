// Same quantized multilingual model is used for offline indexing and browser queries.
export const LOCAL_MODEL='Xenova/paraphrase-multilingual-MiniLM-L12-v2';
export const LOCAL_DIMENSIONS=384;
let extractor;
export async function localEmbed(text){
 const {pipeline,env}=await import('@huggingface/transformers');
 env.localModelPath=(process.env.RAG_MODEL_CACHE||process.env.HOME+'/.cache/chuangan-embedding')+'/';env.allowRemoteModels=false;
 extractor??=pipeline('feature-extraction',LOCAL_MODEL,{dtype:'q8'});
 const output=await (await extractor)(text,{pooling:'mean',normalize:true,truncation:true,max_length:512});
 return Array.from(output.data);
}
