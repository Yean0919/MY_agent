# 名称
bug-hunt

# 描述
Bug 排查辅助技能。分析 Python 代码中的常见 Bug 模式，包括类型错误、未处理异常、资源泄漏、并发问题等。提供问题定位和修复建议。

# 版本
1.0.0

# 使用方法
```bash
# 扫描单个文件
python skills/bug-hunt/scripts/hunt.py --file src/main.py

# 扫描目录
python skills/bug-hunt/scripts/hunt.py --dir src/

# 只检测特定类型的 Bug
python skills/bug-hunt/scripts/hunt.py --file src/main.py --type resource-leak,null-access

# 输出 JSON 格式
python skills/bug-hunt/scripts/hunt.py --dir src/ --format json
```

# 参数
- `--file`: 要扫描的文件路径
- `--dir`: 要扫描的目录路径
- `--type`: 只检测特定类型的 Bug，逗号分隔
- `--format`: 输出格式: text (默认), json, markdown
- `--severity`: 最低严重度: low, medium (默认), high

# 支持的 Bug 类型

| Bug 类型 | 说明 | 严重度 | 示例 |
|----------|------|--------|------|
| null-access | 可能的空值访问 | high | 未检查 None 就调用方法 |
| resource-leak | 资源泄漏 | high | 打开文件/连接后未关闭 |
| type-mismatch | 类型不匹配 | medium | 字符串和数字混用 |
| exception-swallow | 异常吞没 | high | 空 except 或 pass |
| index-out-of-range | 可能的越界访问 | medium | 未检查长度就索引 |
| import-error | 导入问题 | high | 导入不存在的模块 |
| unused-variable | 未使用变量 | low | 定义了但从未使用 |
| mutable-default | 可变默认参数 | medium | 列表/字典作为默认值 |
| string-format | 字符串格式化问题 | low | f-string 或 format 使用不当 |
