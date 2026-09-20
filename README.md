# 创安睿控 AI 智能体

可交互的静态网页演示，包含聊天工作台、四位演示助手、示例知识库、引用来源与本次页面内的对话记录。

## 演示范围

回答由预设内容生成，尚未接入真实大模型、公司数据或设备。知识条目为演示内容；刷新页面会清空对话。

## GitHub Pages

在仓库 Settings → Pages 中选择 Deploy from a branch，分支 main，目录 / (root)，然后保存。以后推送 main 会自动发布。

## 本地运行

直接打开 index.html，或在目录中运行 `python3 -m http.server 8080`，访问 http://localhost:8080。

## 文件

- index.html：页面结构
- styles.css：样式与响应式布局
- app.js：交互与演示回答
- .nojekyll：按静态文件发布

不要将 API 密钥或公司私有资料加入前端代码或公开仓库。接入真实模型时，应由服务端保管密钥并实施访问控制。
