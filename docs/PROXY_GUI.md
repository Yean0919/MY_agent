# TCA Proxy - 本地代理配置工具

> 类似 CC-Switch 的本地 LLM 代理配置工具，支持 GUI 界面配置。

---

## 功能特性

- ✅ **GUI 配置界面** - 类似 CC-Switch 的图形界面
- ✅ **多提供商支持** - OpenAI、Anthropic、自定义 API
- ✅ **代理服务器** - 本地代理转发请求
- ✅ **配置管理** - JSON 配置文件，持久化存储
- ✅ **一键启动** - Windows 批处理脚本

---

## 快速开始

### 1. 启动 GUI 配置界面

```bash
# 方法一：使用批处理脚本
scripts\start_gui.bat

# 方法二：直接运行
python -m src.gui.proxy_gui
```

### 2. 配置代理

1. 打开 GUI 界面
2. 配置代理主机和端口（默认 127.0.0.1:8080）
3. 添加 LLM 提供商（OpenAI、Anthropic 等）
4. 输入 API Key
5. 激活要使用的提供商
6. 保存配置

### 3. 启动代理服务器

```bash
# 方法一：使用批处理脚本
scripts\start_proxy.bat

# 方法二：直接运行
python -m src.server.proxy
```

### 4. 配置 Claude Code

```bash
# 在 Claude Code 中设置使用本地代理
export ANTHROPIC_API_URL=http://127.0.0.1:8080
export ANTHROPIC_API_KEY=your_api_key
```

---

## 界面截图

### 主界面

```
┌─────────────────────────────────────────────────────────┐
│  TCA Proxy - 本地代理配置                                │
├─────────────────────────────────────────────────────────┤
│  代理配置                                                │
│  ☑ 启用代理                                              │
│  主机: [127.0.0.1]          端口: [8080]                │
│  状态: 未启动                                             │
├─────────────────────────────────────────────────────────┤
│  LLM 提供商配置                                          │
│  ┌─────────┬────────────────────────┬──────────┬──────┐ │
│  │ 名称    │ API URL                │ API Key  │ 激活 │ │
│  ├─────────┼────────────────────────┼──────────┼──────┤ │
│  │ OpenAI  │ https://api.openai.com │ ****     │      │ │
│  │ Anthropic│ https://api.anthropic │ ****     │  ✓   │ │
│  │ Custom  │                        │          │      │ │
│  └─────────┴────────────────────────┴──────────┴──────┘ │
│  [添加] [编辑] [删除] [设为激活]                         │
├─────────────────────────────────────────────────────────┤
│  就绪                                                    │
└─────────────────────────────────────────────────────────┘
```

---

## 配置文件

配置文件保存在 `config/proxy_config.json`：

```json
{
  "proxy": {
    "host": "127.0.0.1",
    "port": 8080,
    "enabled": true
  },
  "providers": [
    {
      "name": "OpenAI",
      "url": "https://api.openai.com/v1",
      "api_key": "sk-xxx",
      "active": false
    },
    {
      "name": "Anthropic",
      "url": "https://api.anthropic.com/v1",
      "api_key": "sk-xxx",
      "active": true
    }
  ]
}
```

---

## 使用场景

### 场景 1：切换 LLM 提供商

1. 在 GUI 中添加多个提供商
2. 点击"设为激活"切换当前使用的提供商
3. 代理服务器自动转发到激活的提供商

### 场景 2：本地开发调试

1. 启动代理服务器
2. 配置 Claude Code 使用本地代理
3. 所有请求经过本地代理，方便调试和监控

### 场景 3：API 密钥管理

1. 在 GUI 中安全存储 API Key
2. 代理服务器自动添加认证头
3. 避免在代码中硬编码密钥

---

## 技术栈

- **GUI**: tkinter（Python 标准库）
- **服务器**: FastAPI + uvicorn
- **HTTP 客户端**: httpx
- **配置**: JSON 文件

---

## 依赖

```bash
pip install fastapi uvicorn httpx pydantic
```

---

## 常见问题

### Q: GUI 界面打不开？

A: 确保安装了 tkinter（Python 标准库自带）。如果是 Linux，可能需要安装 `python3-tk`。

### Q: 代理服务器启动失败？

A: 检查端口是否被占用，默认端口 8080，可以在 GUI 中修改。

### Q: 如何配置 Claude Code 使用代理？

A: 设置环境变量：
```bash
export ANTHROPIC_API_URL=http://127.0.0.1:8080
```

---

## 许可证

MIT License
