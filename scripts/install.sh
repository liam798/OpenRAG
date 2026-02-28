#!/usr/bin/env bash
set -e

OPENRAG_REPO="${OPENRAG_REPO:-https://github.com/liam798/OpenRAG.git}"
OPENRAG_HOME="${OPENRAG_HOME:-$HOME/OpenRAG}"

echo "==> OpenRAG 一键部署"
echo "    安装目录: $OPENRAG_HOME"
echo ""

if ! command -v docker &>/dev/null; then
  echo "错误: 请先安装 Docker (https://docs.docker.com/get-docker/)" >&2
  exit 1
fi
if ! docker compose version &>/dev/null; then
  echo "错误: 请先安装 Docker Compose (https://docs.docker.com/compose/install/)" >&2
  exit 1
fi

if [[ -d "$OPENRAG_HOME" && -f "$OPENRAG_HOME/docker-compose.yml" ]]; then
  echo "==> 使用已有目录: $OPENRAG_HOME"
  cd "$OPENRAG_HOME"
  git pull --rebase 2>/dev/null || true
else
  echo "==> 克隆仓库..."
  git clone --depth 1 "$OPENRAG_REPO" "$OPENRAG_HOME"
  cd "$OPENRAG_HOME"
fi

echo "==> 启动 PostgreSQL (Docker)..."
docker compose up -d

if [[ ! -f backend/.env ]]; then
  echo "==> 生成 backend/.env"
  cp backend/.env.example backend/.env
  echo "    请编辑 backend/.env 填写 OPENAI_API_KEY 等配置。"
fi

echo "==> 执行数据库迁移..."
(cd backend && pip install -q -r requirements.txt 2>/dev/null; alembic upgrade head)

echo ""
echo "==> 部署就绪。请在本机两个终端中分别启动后端与前端："
echo ""
echo "  终端 1 - 后端:"
echo "    cd $OPENRAG_HOME/backend && uvicorn app.main:app --reload"
echo ""
echo "  终端 2 - 前端:"
echo "    cd $OPENRAG_HOME/frontend && npm install && npm run dev"
echo ""
echo "  浏览器访问: http://localhost:3000"
echo ""
