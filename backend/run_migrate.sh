#!/bin/sh
# 若登录报 500，请先执行本脚本应用迁移
cd "$(dirname "$0")"
alembic upgrade head
