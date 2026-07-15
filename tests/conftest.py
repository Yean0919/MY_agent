"""pytest fixtures"""

import pytest


@pytest.fixture
def sample_state():
    """示例 Agent 状态"""
    return {
        "session_id": "test_session",
        "task": "test_task",
        "context": {},
        "messages": [],
    }


@pytest.fixture
def sample_message():
    """示例消息"""
    return {
        "role": "user",
        "content": "Hello, world!",
    }
