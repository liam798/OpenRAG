---
name: openrag
version: 0.2.0
description: 查询 OpenRAG 知识库进行 RAG 问答。当用户需要从公司/项目知识库检索信息、回答问题或引用文档时使用。
---

# OpenRAG 知识库查询

面向 AI Agent 接入的 OpenRAG：从知识库检索并回答用户问题。

## 使用前：注册、登录、获取 API Key

**若未登录，请提示用户：** 请先注册并登录 OpenRAG，在面板右上角用户菜单中点击「API Key」查看，将 API Key 提供给 Agent 使用。

### 1. 注册与登录

用户需先访问 OpenRAG 前端完成注册和登录。

### 2. 在面板查看 API Key

登录后，点击右上角用户名 → **API Key**，即可查看或生成 API Key。将 API Key 复制给 Agent 使用。

### 3. Agent 通过 API Key 调用

Agent 在请求时需在 Header 中携带：

```
X-API-Key: <用户的API_Key>
```

## API 说明

认证：`X-API-Key: <api_key>` 或 `Authorization: Bearer <jwt>`

- `POST /api/knowledge-bases/query` - 多知识库 RAG 问答
- `POST /api/knowledge-bases/{kb_id}/query` - 指定知识库 RAG 问答
- `GET /api/knowledge-bases` - 列出知识库

详见在线版 `http://localhost:3000/skill.md`。
