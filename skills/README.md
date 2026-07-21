# Skills 目录

本目录包含 MY_agent 的所有技能定义。每个技能是一个独立的工具，可通过命令行或 Agent 调用。

## 可用技能

| 技能 | 说明 | 用途 |
|------|------|------|
| [code-review](code-review/) | 自动代码审查 | 多维度审查代码质量，发现问题和改进建议 |
| [test-gen](test-gen/) | 测试生成 | 分析源码自动生成 pytest 测试用例 |
| [refactor](refactor/) | 重构分析 | 检测代码异味，提供重构建议 |
| [api-doc](api-doc/) | API 文档生成 | 扫描路由自动生成接口文档 |
| [bug-hunt](bug-hunt/) | Bug 排查 | 检测常见 Bug 模式和潜在问题 |
| [example_skill](example_skill/) | 示例技能 | 展示如何创建技能（模板） |
| [repo-docs-resume](repo-docs-resume/) | 项目文档生成 | 从代码仓库生成项目文档和简历经历 |

## 快速使用

```bash
# 代码审查
python skills/code-review/scripts/review.py --file src/main.py

# 生成测试
python skills/test-gen/scripts/generate.py --file src/utils.py

# 重构分析
python skills/refactor/scripts/analyze.py --dir src/

# API 文档
python skills/api-doc/scripts/generate.py --dir src/api/routes/ --format markdown

# Bug 排查
python skills/bug-hunt/scripts/hunt.py --file src/main.py
```

## 技能结构

每个技能是一个目录，包含：

```
skill_name/
├── SKILL.md          # 技能定义文件（必需）
└── scripts/          # 脚本目录（可选）
    └── script.py     # 可执行脚本
```

## SKILL.md 格式

```markdown
# 名称
skill_name

# 描述
技能的描述

# 版本
1.0.0

# 使用方法
```bash
python skills/skill_name/scripts/script.py --args
```

# 参数
- `--param`: 参数描述
```

## 创建新技能

1. 在 `skills/` 下创建目录
2. 编写 `SKILL.md` 定义文件
3. 在 `scripts/` 下编写实现脚本
4. 更新本 README 的技能列表
