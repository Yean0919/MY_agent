# 名称
code-review

# 描述
自动代码审查技能。对指定文件或目录进行多维度代码审查，输出问题清单和改进建议。支持 Python/JS/TS 等语言，关注正确性、性能、安全性和可维护性。

# 版本
1.0.0

# 使用方法
```bash
# 审查单个文件
python skills/code-review/scripts/review.py --file src/main.py

# 审查整个目录
python skills/code-review/scripts/review.py --dir src/

# 指定审查维度
python skills/code-review/scripts/review.py --file src/main.py --focus security,performance

# 输出 JSON 格式
python skills/code-review/scripts/review.py --file src/main.py --format json
```

# 参数
- `--file`: 要审查的单个文件路径
- `--dir`: 要审查的目录路径（递归扫描）
- `--focus`: 审查维度，逗号分隔。可选: correctness, performance, security, maintainability, style
- `--format`: 输出格式，可选: text (默认), json, markdown
- `--max-issues`: 最大问题数，默认 20

# 审查维度说明

| 维度 | 说明 | 示例问题 |
|------|------|----------|
| correctness | 正确性 | 逻辑错误、边界条件未处理、异常吞没 |
| performance | 性能 | 不必要的循环、内存泄漏、N+1 查询 |
| security | 安全性 | SQL注入、硬编码密钥、不安全的反序列化 |
| maintainability | 可维护性 | 函数过长、重复代码、缺少注释 |
| style | 代码风格 | 命名不规范、导入混乱、格式问题 |
