# 名称
test-gen

# 描述
自动单元测试生成技能。分析 Python 源文件中的函数和类，自动生成 pytest 测试代码。支持正常路径、边界条件和异常场景的测试用例生成。

# 版本
1.0.0

# 使用方法
```bash
# 为单个文件生成测试
python skills/test-gen/scripts/generate.py --file src/utils.py

# 指定输出路径
python skills/test-gen/scripts/generate.py --file src/utils.py --output tests/test_utils.py

# 为整个目录生成测试
python skills/test-gen/scripts/generate.py --dir src/ --output-dir tests/

# 只生成特定函数的测试
python skills/test-gen/scripts/generate.py --file src/utils.py --function calculate_sum
```

# 参数
- `--file`: 要分析的源文件路径
- `--dir`: 要分析的目录路径（递归扫描所有 .py 文件）
- `--output`: 测试文件输出路径（默认: tests/test_<原文件名>）
- `--output-dir`: 批量生成时的输出目录
- `--function`: 只为指定函数生成测试
- `--style`: 测试风格，可选: pytest (默认), unittest

# 生成的测试类型

| 测试类型 | 说明 | 示例 |
|----------|------|------|
| 正常路径 | 验证函数的基本功能 | 正确输入得到预期输出 |
| 边界条件 | 测试边界值 | 空列表、零值、最大值 |
| 异常场景 | 验证错误处理 | 无效输入抛出正确异常 |
| 类型检查 | 验证类型约束 | 传入错误类型时的行为 |
