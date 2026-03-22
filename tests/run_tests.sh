#!/usr/bin/env bash
# ───────────────────────────────────────────────
# AI 写作助手 — 统一测试运行脚本
# ───────────────────────────────────────────────
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPORTS_DIR="$ROOT_DIR/reports"
BACKEND_DIR="$ROOT_DIR/../backend"
FRONTEND_DIR="$ROOT_DIR/../frontend"

# 确保 reports 目录存在
mkdir -p "$REPORTS_DIR"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

usage() {
    echo "用法: $0 [all|backend|frontend]"
    echo ""
    echo "  all       运行全部测试（默认）"
    echo "  backend   只运行后端 pytest 测试"
    echo "  frontend  只运行前端 vitest 测试"
    echo ""
    echo "测试报告输出到: $REPORTS_DIR/"
}

run_backend() {
    echo -e "${CYAN}━━━ 后端测试 (pytest) ━━━${NC}"
    cd "$BACKEND_DIR"
    uv run pytest --tb=short "$@"
    echo -e "${GREEN}✔ 后端测试完成，报告: tests/reports/backend_report.html${NC}"
}

run_frontend() {
    echo -e "${CYAN}━━━ 前端测试 (vitest) ━━━${NC}"
    cd "$FRONTEND_DIR"
    npx vitest run "$@"
    echo -e "${GREEN}✔ 前端测试完成，报告: tests/reports/frontend_report.html${NC}"
}

TARGET="${1:-all}"

case "$TARGET" in
    all)
        run_backend
        echo ""
        run_frontend
        echo ""
        echo -e "${GREEN}━━━ 全部测试完成 ━━━${NC}"
        ;;
    backend)
        shift || true
        run_backend "$@"
        ;;
    frontend)
        shift || true
        run_frontend "$@"
        ;;
    -h|--help)
        usage
        ;;
    *)
        echo -e "${RED}未知参数: $TARGET${NC}"
        usage
        exit 1
        ;;
esac
