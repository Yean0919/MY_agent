#!/bin/bash
# ============================================================
# YEAN — Terminal Coding Agent 环境初始化脚本
# 在 data_analysis conda 环境下部署
# ============================================================

set -e

CONDA_ENV="${CONDA_ENV:-data_analysis}"
CONDA_ROOT="${CONDA_ROOT:-/opt/anaconda3}"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "🚀 初始化 YEAN (Terminal Coding Agent) 环境..."
echo "   Conda 环境: $CONDA_ENV"
echo "   项目目录: $PROJECT_ROOT"
echo ""

# 检查 conda
if ! command -v conda &> /dev/null; then
    echo "❌ 找不到 conda，请设置 CONDA_ROOT 环境变量"
    exit 1
fi

# 创建或激活 conda 环境
if ! conda env list | grep -q "^$CONDA_ENV "; then
    echo "📦 创建 conda 环境: $CONDA_ENV"
    conda create -n "$CONDA_ENV" python=3.10 -y
fi

# 激活环境
echo "🔧 激活 conda 环境..."
# shellcheck disable=SC1091
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV"

# 升级 pip
echo "⬆️ 升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "📥 安装依赖..."
cd "$PROJECT_ROOT"
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 安装项目（可编辑模式）
echo "📦 安装 YEAN（可编辑模式）..."
pip install -e .

# 配置环境变量
if [ ! -f ".env" ]; then
    echo "⚙️ 创建 .env 文件..."
    cp .env.example .env
    echo "请编辑 .env 文件，填入你的 API Key"
fi

# 安装 pre-commit
echo "🔒 安装 pre-commit..."
pre-commit install 2>/dev/null || true

echo ""
echo "✅ 环境初始化完成！"
echo ""
echo "下一步："
echo "  1. 编辑 .env 文件，填入 API Key"
echo "  2. 运行 'conda activate $CONDA_ENV'"
echo "  3. 运行 'yean' 启动交互模式"
echo "  4. 运行 'yean \"你的任务\"' 单次执行"
