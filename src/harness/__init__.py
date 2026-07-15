"""Harness Engineering — 终端交互执行引擎。

所有终端输入统一交给 AgentLoop（TAOR 循环），由 LLM 自己决定
是直接回复还是调用工具，不再手动路由（闲聊/解释/工具分流）。
"""
