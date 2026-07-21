# 名称
api-doc

# 描述
API 文档自动生成技能。扫描 FastAPI/Flask 路由定义，自动生成 API 文档，包括接口列表、请求参数、响应格式和示例。支持 OpenAPI 规范输出。

# 版本
1.0.0

# 使用方法
```bash
# 扫描单个路由文件
python skills/api-doc/scripts/generate.py --file src/api/routes/chat.py

# 扫描整个路由目录
python skills/api-doc/scripts/generate.py --dir src/api/routes/

# 输出 OpenAPI YAML 格式
python skills/api-doc/scripts/generate.py --dir src/api/routes/ --format openapi

# 输出 Markdown 文档
python skills/api-doc/scripts/generate.py --dir src/api/routes/ --format markdown
```

# 参数
- `--file`: 路由文件路径
- `--dir`: 路由目录路径
- `--format`: 输出格式: text (默认), json, markdown, openapi
- `--output`: 输出文件路径（默认输出到终端）
- `--title`: API 文档标题

# 支持的框架

| 框架 | 说明 |
|------|------|
| FastAPI | 自动解析 @app.get/post/put/delete 装饰器 |
| Flask | 自动解析 @app.route 装饰器 |
| APIRouter | 解析 FastAPI 子路由 |

# 生成的文档内容

- 接口路径和方法（GET/POST/PUT/DELETE）
- 路径参数、查询参数、请求体
- 响应状态码和格式
- Pydantic 模型定义
- 接口描述和标签
