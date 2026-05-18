# Load .env if it exists
-include .env
export

.PHONY: help install dev-install run-all stop-all run-gateway run-data run-forecaster \
        run-route run-anomaly run-affinity run-simulator run-mcp run-chatbot \
        run-dashboard launch docker-build docker-up docker-down docker-logs test clean

# Default target
help:
	@echo "DarkStore Analytics Platform - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install        - Install all service dependencies"
	@echo "  make run-all        - Run all services locally (requires multiple terminals)"
	@echo "  make stop-all       - Stop all running services"
	@echo ""
	@echo "Individual Services:"
	@echo "  make run-gateway    - Run API Gateway (port 8000)"
	@echo "  make run-data       - Run Data Service (port 8001)"
	@echo "  make run-forecaster - Run Forecaster Service (port 8002)"
	@echo "  make run-route      - Run Route Optimizer Service (port 8003)"
	@echo "  make run-anomaly    - Run Anomaly Detector Service (port 8004)"
	@echo "  make run-affinity   - Run Affinity Analyzer Service (port 8005)"
	@echo "  make run-simulator  - Run Event Simulator Service (port 8006)"
	@echo "  make run-mcp        - Run MCP Server (port 8010)"
	@echo "  make run-chatbot    - Run AI Chatbot (port 8020)"
	@echo "  make run-dashboard  - Run Dashboard dev server (port 3000)"
	@echo "  make launch         - Start everything and open dashboard in browser"
	@echo "  make stop-all       - Stop all running services"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Build all Docker images"
	@echo "  make docker-up      - Start all services with Docker Compose"
	@echo "  make docker-down    - Stop all Docker services"
	@echo "  make docker-logs    - View Docker logs"
	@echo ""
	@echo "Other:"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean up temporary files"

# Install dependencies for all services
install:
	@echo "Installing dependencies for all services..."
	cd services/api-gateway && pip install -r requirements.txt
	cd services/data-service && pip install -r requirements.txt
	cd services/forecaster-service && pip install -r requirements.txt
	cd services/route-optimizer-service && pip install -r requirements.txt
	cd services/anomaly-detector-service && pip install -r requirements.txt
	cd services/affinity-analyzer-service && pip install -r requirements.txt
	cd services/event-simulator-service && pip install -r requirements.txt
	cd mcp-server && pip install -r requirements.txt
	cd chatbot && pip install -r requirements.txt
	@echo "All dependencies installed!"

# Run individual services
run-data:
	cd services/data-service && uvicorn src.main:app --reload --port 8001

run-forecaster:
	cd services/forecaster-service && uvicorn src.main:app --reload --port 8002

run-route:
	cd services/route-optimizer-service && uvicorn src.main:app --reload --port 8003

run-anomaly:
	cd services/anomaly-detector-service && uvicorn src.main:app --reload --port 8004

run-affinity:
	cd services/affinity-analyzer-service && uvicorn src.main:app --reload --port 8005

run-simulator:
	cd services/event-simulator-service && uvicorn src.main:app --reload --port 8006

run-gateway:
	cd services/api-gateway && uvicorn src.main:app --reload --port 8000

run-mcp:
	cd mcp-server && python main.py

run-chatbot:
	cd chatbot && uvicorn main:app --reload --port 8020

run-dashboard:
	cd dashboard && npm run dev

# Path to venv uvicorn (auto-detected or fallback to PATH)
VENV_DIR := $(shell pwd)/venv
UVICORN := $(shell if [ -x $(VENV_DIR)/bin/uvicorn ]; then echo $(VENV_DIR)/bin/uvicorn; else which uvicorn 2>/dev/null; fi)
PYTHON := $(shell if [ -x $(VENV_DIR)/bin/python ]; then echo $(VENV_DIR)/bin/python; else which python3 2>/dev/null; fi)

# Launch everything: all backends + dashboard, then open browser
launch:
	@echo "=== DarkStore Analytics Platform ==="
	@echo ""
	@# Check uvicorn is available
	@if [ -z "$(UVICORN)" ]; then \
		echo "Error: uvicorn not found. Run 'make install' first or create a venv."; \
		exit 1; \
	fi
	@echo "  Using: $(UVICORN)"
	@# Ensure dashboard dependencies are installed
	@if [ ! -d dashboard/node_modules ]; then \
		echo "  Installing dashboard dependencies..."; \
		cd dashboard && npm install --silent; \
	fi
	@echo "  Starting all services..."
	@mkdir -p .pids logs
	@# Start backend services in background
	@cd services/data-service && nohup $(UVICORN) src.main:app --port 8001 > ../../logs/data.log 2>&1 & echo $$! > .pids/data.pid
	@cd services/forecaster-service && nohup $(UVICORN) src.main:app --port 8002 > ../../logs/forecaster.log 2>&1 & echo $$! > .pids/forecaster.pid
	@cd services/route-optimizer-service && nohup $(UVICORN) src.main:app --port 8003 > ../../logs/route.log 2>&1 & echo $$! > .pids/route.pid
	@cd services/anomaly-detector-service && nohup $(UVICORN) src.main:app --port 8004 > ../../logs/anomaly.log 2>&1 & echo $$! > .pids/anomaly.pid
	@cd services/affinity-analyzer-service && nohup $(UVICORN) src.main:app --port 8005 > ../../logs/affinity.log 2>&1 & echo $$! > .pids/affinity.pid
	@cd services/event-simulator-service && nohup $(UVICORN) src.main:app --port 8006 > ../../logs/simulator.log 2>&1 & echo $$! > .pids/simulator.pid
	@cd services/api-gateway && nohup $(UVICORN) src.main:app --port 8000 > ../../logs/gateway.log 2>&1 & echo $$! > .pids/gateway.pid
	@cd chatbot && nohup $(UVICORN) main:app --port 8020 > ../logs/chatbot.log 2>&1 & echo $$! > .pids/chatbot.pid
	@echo "  [1/3] Backend services starting..."
	@sleep 6
	@# Start dashboard in background
	@cd dashboard && nohup npx vite --port 3000 > ../logs/dashboard.log 2>&1 & echo $$! > .pids/dashboard.pid
	@echo "  [2/3] Dashboard starting..."
	@sleep 3
	@# Verify services came up
	@echo "  [3/3] Checking services..."
	@UP=0; for port in 8001 8002 8003 8004 8005 8006 8000 8020 3000; do \
		if lsof -ti:$$port > /dev/null 2>&1; then UP=$$((UP+1)); fi; \
	done; \
	echo "  $$UP/9 services running"
	@echo ""
	@echo "  Dashboard:    http://localhost:3000"
	@echo "  API Gateway:  http://localhost:8000"
	@echo "  Logs:         ./logs/"
	@echo ""
	@open http://localhost:3000 2>/dev/null || xdg-open http://localhost:3000 2>/dev/null || echo "  Open http://localhost:3000 in your browser"
	@echo "  Run 'make stop-all' to shut everything down."

# Stop all running services
stop-all:
	@echo "Stopping all services..."
	@# Kill by port (most reliable)
	@for port in 3000 8000 8001 8002 8003 8004 8005 8006 8020; do \
		pid=$$(lsof -ti:$$port 2>/dev/null); \
		if [ -n "$$pid" ]; then \
			kill $$pid 2>/dev/null; \
			echo "  Stopped port $$port (PID $$pid)"; \
		fi; \
	done
	@rm -rf .pids 2>/dev/null || true
	@echo "All services stopped."

# Run all services (prints instructions)
run-all:
	@echo "To run all services, open separate terminals and run:"
	@echo ""
	@echo "Terminal 1: make run-data"
	@echo "Terminal 2: make run-forecaster"
	@echo "Terminal 3: make run-route"
	@echo "Terminal 4: make run-anomaly"
	@echo "Terminal 5: make run-affinity"
	@echo "Terminal 6: make run-simulator"
	@echo "Terminal 7: make run-gateway"
	@echo "Terminal 8: make run-mcp (optional)"
	@echo "Terminal 9: make run-chatbot (optional, requires GOOGLE_API_KEY)"
	@echo "Terminal 10: make run-dashboard (React dashboard, port 3000)"
	@echo ""
	@echo "Or use: make docker-up"

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Test endpoints
test:
	@echo "Testing API Gateway health..."
	curl -s http://localhost:8000/health | python -m json.tool
	@echo ""
	@echo "Testing all services health..."
	curl -s http://localhost:8000/health/all | python -m json.tool

# Clean up
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
