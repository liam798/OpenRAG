# OpenRAG - 智能知识库平台

类似 GitHub 仓库概念的 RAG 知识库系统，支持多用户、多知识库与细粒度权限管理。

## 功能特性

- **用户系统**：注册、登录、JWT 认证
- **知识库（仓库）**：每个用户可创建多个知识库，支持公开/私有
- **权限管理**：Owner / Admin / Write / Read 四级权限
- **文档管理**：上传文档，自动分块与向量化
- **智能检索**：基于 RAG 的问答，支持语义搜索
- **Agent 一键接入**：复制 Agent 提示词，即可让你的 Agent 自动接入 OpenRAG 知识库检索

## 技术栈

- **后端**：FastAPI + SQLAlchemy + PostgreSQL + pgvector
- **RAG**：LangChain + OpenAI Embeddings
- **前端**：React + TypeScript + Tailwind CSS

## 快速开始

### 一键部署

已安装 Docker 与 Docker Compose 时，可执行：

```bash
curl -fsSL https://raw.githubusercontent.com/liam798/OpenRAG/main/scripts/install.sh | bash
```

脚本将克隆仓库、启动 PostgreSQL、执行数据库迁移，并提示你在两个终端分别启动后端与前端。完成后访问 http://localhost:3000 使用。

### 环境要求（手动部署）

- Python 3.10+
- PostgreSQL 14+ (需安装 pgvector 扩展)
- Node.js 18+

### 后端启动

```bash
cd backend
cp .env.example .env  # 配置数据库与 OpenAI API Key
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 数据库初始化

确保 PostgreSQL 已安装 pgvector：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## 项目结构

```
OpenRAG/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── api/      # API 路由
│   │   ├── core/     # 配置、安全
│   │   ├── models/   # 数据模型
│   │   ├── schemas/  # Pydantic 模式
│   │   ├── services/ # 业务逻辑
│   │   └── rag/      # RAG 管道
│   └── alembic/      # 数据库迁移
├── frontend/         # React 前端（含 public/skill.md 在线 Skill）
├── skills/openrag/   # Skill 仓库副本（离线参考）
└── README.md
```

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 用户登录 |
| GET | /api/auth/me | 当前用户信息 |
| GET | /api/knowledge-bases | 我的知识库列表 |
| POST | /api/knowledge-bases | 创建知识库 |
| GET | /api/knowledge-bases/{id} | 知识库详情 |
| POST | /api/knowledge-bases/{id}/documents | 上传文档 |
| POST | /api/knowledge-bases/{id}/query | RAG 问答 |
| GET | /api/knowledge-bases/{id}/members | 成员列表 |
| POST | /api/knowledge-bases/{id}/members | 添加成员 |

**API Key**：调用公开接口时使用（用户菜单 → API Key）。Agent 接入时在 API Key 弹窗中点击「复制 Agent 提示词」即可一键让 Agent 接入 OpenRAG。
