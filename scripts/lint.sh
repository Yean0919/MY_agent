#!/bin/bash
# 代码检查脚本

set -e

echo "🔍 运行代码检查..."

# ruff 检查
echo "📝 Ruff 检查..."
ruff check src/ tests/

# ruff 格式化
echo "🎨 Ruff 格式化..."
ruff format src/ tests/

# mypy 类型检查
echo "🔎 Mypy 类型检查..."
mypy src/

echo "✅ 代码检查完成！"
