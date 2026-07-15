"""API 路由单元测试"""

from fastapi.testclient import TestClient

from src.api.app import app

client = TestClient(app)


class TestHealthRoutes:
    """健康检查路由测试"""

    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health/")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestRootRoute:
    """根路由测试"""

    def test_root(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Terminal CodingAgent API" in response.json()["message"]
