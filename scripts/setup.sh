#!/bin/bash
# 环境初始化脚本

set -e

echo "🚀 初始化 Terminal CodingAgent 环境..."

# 检查 Python 版本
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

# 创建虚拟环境
if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    python -m venv .venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate

# 升级 pip
echo "⬆️ 升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 配置环境变量
if [ ! -f ".env" ]; then
    echo "⚙️ 创建 .env 文件..."
    cp .env.example .env
    echo "请编辑 .env 文件，填入你的 API Key"
fi

# 安装 pre-commit
echo "🔒 安装 pre-commit..."
pre-commit install

echo "✅ 环境初始化完成！"
echo ""
echo "下一步："
echo "  1. 编辑 .env 文件，填入 API Key"
echo "  2. 运行 'make test' 测试"
echo "  3. 运行 'make run' 启动服务"
