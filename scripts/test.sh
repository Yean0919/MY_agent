#!/bin/bash
# 测试运行脚本

set -e

echo "🧪 运行测试..."

# 运行单元测试
echo "📦 单元测试..."
pytest tests/unit/ -v

# 运行集成测试
echo "🔗 集成测试..."
pytest tests/integration/ -v

# 运行端到端测试
echo "🎯 端到端测试..."
pytest tests/e2e/ -v

echo "✅ 测试完成！"
