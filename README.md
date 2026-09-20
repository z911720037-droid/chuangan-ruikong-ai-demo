# 创安睿控 AI · 产品手册知识问答

网页入口：https://z911720037-droid.github.io/chuangan-ruikong-ai-demo/

真实问答：https://chuangan-ruikong-ai-demo.z911720037.chatgpt.site/ （保留登录访问）

## 功能

- 5 份公司提供的手册：CA100、CA700、600U、CL100、CL200，共 759 个 PDF 物理页、785 个检索片段。
- 本地多语言嵌入模型 + 关键词混合检索；DeepSeek 根据检索片段生成真实回答。不调用 OpenAI。
- 回答附可点击的原文与 PDF 页码；没有依据时说明，型号或 CL200 部件不明确时追问。
- 模型服务失败时显示错误，不生成预设替代回答。每次问题独立检索，追问需带上型号和条件。

GitHub Pages 负责公开入口；真实问答需要后端保护 DeepSeek 密钥。原始 PDF、密钥、数据库和完整语料不提交到公开仓库。原文引用已获资料提供者允许公开展示。

## 本地运行

需要 Node.js 22+、Python 3，以及 `pypdf`、`numpy`。

```sh
npm ci
python knowledge/download_model.py
# 在仓库外建立索引目录
python knowledge/ingest.py --source /path/to/pdfs --output /path/to/private-index
python knowledge/export_index.py --data-dir /path/to/private-index
export RAG_DATA_DIR=/path/to/private-index
node knowledge/reembed.mjs
python knowledge/import_local_vectors.py --data-dir /path/to/private-index
cp .env.example .env
# 在本地 .env 中填写 DEEPSEEK_API_KEY、RAG_DATA_DIR 等，不要提交该文件
npm start
```

打开 `http://127.0.0.1:8787`。浏览器首次从模型发布者下载约 136 MB 的分词器和量化模型，随后利用浏览器缓存并在本机推理；这需要能访问模型托管站点。用户问题和检索到的相关原文会发送到 DeepSeek 用于回答。

嵌入模型：`Xenova/paraphrase-multilingual-MiniLM-L12-v2`，固定版本 `2c4055b12046f11709e9df2c122e59ffbdc2f900`，384 维，q8、mean pooling、归一化。文档向量在本机离线生成并写入 SQLite；问题向量在浏览器本机计算。

## 检查

```sh
npm test
npm run test:live
```

真实测试需要本地语料和有效 DeepSeek 密钥，会产生 API 调用。测试覆盖参数、故障代码、CL200 不同部件、缺型号、不存在的型号/参数、报价缺依据以及指令干扰。完整结果写入 `RAG_DATA_DIR`。固定测试通过不代表全部问题均准确，设备操作仍需核对对应手册。

## 部署

仓库根目录为 GitHub Pages 静态页面。后端为 `server/handler.mjs` 的 Worker 处理器，由 `knowledge/build_worker.py` 打包手册索引和网页资源到已有私有服务。后端只配置 `DEEPSEEK_API_KEY`（secret），可选 `DEEPSEEK_MODEL`，默认 `deepseek-flash`。

服务保持账号访问限制，并附加短时限流；内存限流不是全局用量额度。公开开放付费 API 前应增加持久化配额。不要把生成的含完整语料的 Worker 包或 `.env` 上传到这个仓库。
