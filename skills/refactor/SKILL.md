# 名称
refactor

# 描述
代码重构建议技能。分析 Python 代码结构，识别代码异味（Code Smells），提供具体的重构建议和改进方案。支持提取方法、消除重复、简化条件逻辑等重构模式。

# 版本
1.0.0

# 使用方法
```bash
# 分析单个文件
python skills/refactor/scripts/analyze.py --file src/main.py

# 分析目录
python skills/refactor/scripts/analyze.py --dir src/

# 只关注特定类型的代码异味
python skills/refactor/scripts/analyze.py --file src/main.py --smell long-method,duplication

# 自动应用简单的重构（实验性）
python skills/refactor/scripts/analyze.py --file src/main.py --auto-fix
```

# 参数
- `--file`: 要分析的文件路径
- `--dir`: 要分析的目录路径
- `--smell`: 只检测特定类型的代码异味，逗号分隔
- `--auto-fix`: 自动应用安全的重构（实验性功能）
- `--format`: 输出格式: text (默认), json, markdown

# 支持的代码异味检测

| 代码异味 | 说明 | 重构策略 |
|----------|------|----------|
| long-method | 函数过长（>50行） | 提取方法 (Extract Method) |
| long-parameter | 参数过多（>5个） | 引入参数对象 (Introduce Parameter Object) |
| duplication | 重复代码 | 提取公共方法 |
| deep-nesting | 嵌套过深（>4层） | 卫语句 (Guard Clauses) |
| god-class | 类过大（>300行） | 提取类 (Extract Class) |
| magic-number | 魔法数字 | 提取常量 (Extract Constant) |
| dead-code | 未使用的代码 | 直接删除 |
| complex-condition | 复杂条件表达式 | 提取方法简化 |
