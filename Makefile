.PHONY: install lint test run dashboard clean

# 安装依赖
install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# 代码检查
lint:
	ruff check src/ tests/
	ruff format src/ tests/
	mypy src/

# 运行测试
test:
	pytest tests/ -v --cov=src --cov-report=term-missing

# 运行测试（无覆盖率）
test-fast:
	pytest tests/ -v

# 启动 API 服务
run:
	uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload

# 启动可视化面板
dashboard:
	streamlit run src/agents/visualization.py

# 清理缓存
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/

# 环境初始化
setup:
	python -m venv .venv
	@echo "请激活虚拟环境："
	@echo "  Linux/Mac: source .venv/bin/activate"
	@echo "  Windows: .venv\Scripts\activate"

# 配置环境变量
config:
	cp .env.example .env
	@echo "请编辑 .env 文件，填入你的 API Key"

# 完整初始化
init: setup config install

# 帮助
help:
	@echo "可用命令："
	@echo "  make install    - 安装依赖"
	@echo "  make lint       - 代码检查"
	@echo "  make test       - 运行测试"
	@echo "  make run        - 启动 API 服务"
	@echo "  make dashboard  - 启动可视化面板"
	@echo "  make clean      - 清理缓存"
	@echo "  make init       - 完整初始化"
