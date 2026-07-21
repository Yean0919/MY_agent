# Output Templates

## Product Development Document

Use this structure for `产品开发文档.md`:

```markdown
# <项目名> - 产品开发文档

## 1. 项目定位
## 2. 产品目标
## 3. 目标用户
## 4. 产品范围
### 4.1 已实现能力
### 4.2 当前限制
## 5. 核心业务流程
## 6. 功能模块规划
## 7. 关键非功能要求
## 8. 里程碑建议
## 9. 开发风险与建议
```

Focus on product value, user roles, current implementation state, and realistic next milestones.

## System Architecture Document

Use this structure for `系统架构文档.md`:

```markdown
# <项目名> - 系统架构文档

## 1. 架构概览
## 2. 技术栈
## 3. 总体架构图
## 4. 后端分层
## 5. 核心运行流程
## 6. 数据模型
## 7. API 概览
## 8. RAG / AI 架构
## 9. 部署架构
## 10. 配置与环境变量
## 11. 安全架构
## 12. 可观测性
## 13. 架构风险与改进点
```

Use Mermaid diagrams for component relationships and key flows.

## Requirements Document

Use this structure for `需求文档.md`:

```markdown
# <项目名> - 需求文档

## 1. 文档说明
## 2. 产品背景
## 3. 业务目标
## 4. 角色与权限
## 5. 功能需求
### 5.1 用户与认证
### 5.2 核心业务功能
### 5.3 AI / RAG / Agent 能力
### 5.4 管理后台
## 6. 接口契约需求
## 7. 非功能需求
### 7.1 性能
### 7.2 可用性
### 7.3 安全
### 7.4 合规与审计
## 8. 数据一致性需求
## 9. 验收测试建议
## 10. 待补齐需求
```

Functional requirements should include IDs, priority, current status when useful, and acceptance criteria.

## Resume Project Experience

Use this structure for `简历项目经历.md`:

```markdown
# 简历项目经历 - <项目名>

## <项目名>

**项目角色：<角色>**  
**项目类型：<类型>**  
**项目周期：可按实际经历填写**  
**项目地址：** `<repo url if available>`

### 项目背景
### 技术栈
### 项目职责
### 项目成果
### 简历精简版
### 面试展开版
```

Resume wording rules:

- Start responsibility bullets with active engineering verbs such as `负责`、`设计并实现`、`封装`、`参与`、`建设`.
- Keep responsibilities tied to concrete modules and technologies.
- Keep results defensible: `搭建了...链路`、`实现了...能力`、`提供了...部署资源`.
- Do not invent metrics. If metrics are needed, write placeholders such as `可按实际压测结果补充`.
