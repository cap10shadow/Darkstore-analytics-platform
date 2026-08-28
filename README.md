# DarkStore Analytics Platform

A microservices-based analytics platform for dark store (dark warehouse) operations. Provides AI-powered demand forecasting, route optimization, anomaly detection, product affinity analysis, and an intelligent chatbot interface.

## Architecture

```
darkstore-analytics-platform/
├── services/
│   ├── api-gateway/          (Port 8000) — central request router
│   ├── data-service/         (Port 8001) — SQLite data access layer
│   ├── forecaster-service/   (Port 8002) — multi-model demand forecasting
│   ├── route-optimizer-service/ (Port 8003) — warehouse picking route optimizer
│   ├── anomaly-detector-service/ (Port 8004) — Isolation Forest + Z-score detection
│   ├── affinity-analyzer-service/ (Port 8005) — co-purchase analysis
│   └── event-simulator-service/ (Port 8006) — scenario simulation
├── chatbot/                  (Port 8020) — LangGraph + Gemini AI assistant
├── mcp-server/               (Port 8010) — FastMCP server for Claude integration
├── dashboard/                (Port 3000) — React + TypeScript frontend
├── shared/                   — shared Pydantic models
└── data/
    └── dark_store.db         — SQLite database (150 SKUs, 1,900 orders)
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend services | FastAPI, Uvicorn, Pydantic v2 |
| Data / ML | Pandas, NumPy, scikit-learn, statsmodels, SciPy |
| AI / LLM | LangGraph, LangChain, Google Gemini 2.0 Flash |
| MCP | FastMCP |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS 4, Recharts |
| Database | SQLite (dev) |
| Infra | Docker, Docker Compose |

## Quick Start

### Option A — Local development (all services)

```bash
# 1. Set your Google API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 2. Install dependencies
make install
cd dashboard && npm install

# 3. Start everything and open browser
make launch
```

### Option B — Docker Compose

```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

docker-compose up -d
# Dashboard: http://localhost:3000
```

### Option C — Individual services

```bash
make run-data        # Data service    :8001
make run-forecaster  # Forecaster      :8002
make run-route       # Route optimizer :8003
make run-anomaly     # Anomaly detector:8004
make run-affinity    # Affinity analyzer:8005
make run-simulator   # Event simulator :8006
make run-gateway     # API gateway     :8000
make run-chatbot     # AI chatbot      :8020
make run-dashboard   # React dashboard :3000
```

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | Yes (chatbot) | Google Gemini API key |
| `DATA_SERVICE_URL` | No | Override data service URL |
| `FORECASTER_SERVICE_URL` | No | Override forecaster URL |

## Services Overview

### API Gateway (`/api/v1/*`)
Central entry point. Routes requests to downstream microservices and provides an aggregated `/health/all` check.

### Data Service
Loads SQLite into Pandas DataFrames on startup. Provides KPIs, orders (with pagination), inventory, low-stock analysis, alerts, and staff performance.

### Forecaster Service
Five built-in forecasting models — ARIMA, SARIMA, Holt-Winters, Random Forest, and Gradient Boosting — plus an ensemble and automatic model selection by lowest MAPE.

### Route Optimizer Service
Nearest-Neighbor construction followed by 2-opt local search for warehouse picking routes. The improvement percentage is computed per request against the caller's original pick-list order as the baseline; on the bundled dataset this is typically a 30–45% reduction in travel distance.

### Anomaly Detector Service
Isolation Forest for order anomalies (contamination = 0.05), Z-score analysis for inventory and staff metrics (|z| > 3 and |z| > 2 thresholds). Thresholds are fixed constants rather than tuned per dataset.

### Affinity Analyzer Service
Market-basket analysis computing support, confidence, and lift for co-purchased SKUs, with shelf co-location recommendations derived from the strongest associations.

### Event Simulator Service
Generates synthetic event streams for Normal, Flash Sale, and Supply Delay scenarios. It runs standalone — the generated streams are not currently consumed by the other services, and no throughput or latency measurement is performed.

### AI Chatbot (Port 8020)
ReAct agent built with LangGraph (`langgraph.prebuilt.create_react_agent`) backed by Google Gemini 2.0 Flash. Eight tools covering all analytics capabilities. Conversation history kept per session.

### MCP Server (Port 8010)
FastMCP server exposing 12 tools and 3 resources for direct Claude AI integration.

### Dashboard (Port 3000)
React SPA with eight pages: Overview, Orders, Inventory, Forecast, Routes, Anomalies, Affinity, Simulation. Includes an AI chat panel.

## API Reference

Interactive docs (Swagger UI) are available at each service's `/docs` endpoint when running locally:
- Gateway: http://localhost:8000/docs
- Data: http://localhost:8001/docs
- Forecaster: http://localhost:8002/docs
- Route Optimizer: http://localhost:8003/docs
- Anomaly Detector: http://localhost:8004/docs
- Affinity Analyzer: http://localhost:8005/docs
- Event Simulator: http://localhost:8006/docs
- Chatbot: http://localhost:8020/docs

## Make Commands

```
make help           Show all commands
make install        Install all Python dependencies
make launch         Start everything and open browser
make stop-all       Stop all running services
make docker-up      Start with Docker Compose
make docker-down    Stop Docker services
make docker-logs    Tail Docker logs
make test           Health-check all endpoints
make clean          Remove __pycache__ and .pyc files
```

## Data Model

- **SKUs**: 150 products (SKU01000–SKU01149) across multiple categories
- **Orders**: 1,900 orders with full lifecycle events
- **Shelf locations**: `<AISLE><BAY>-<SHELF>` format (e.g., `A05-3`); 26 aisles × 20 bays × 5 shelves
- **Alerts**: severity levels Critical / High / Medium / Low

The bundled dataset is synthetic and intentionally small — it is sized to demonstrate the analytics pipeline, not to benchmark performance at scale.

## Known Issues / Roadmap

- No authentication / authorization layer.
- SQLite is single-file; replace with PostgreSQL for multi-instance deployments.
- No unit or integration tests.
- Centralised logging and metrics (Prometheus/Grafana) not yet wired up.
