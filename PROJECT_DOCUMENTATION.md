# DarkStore Analytics Platform

A microservices-based analytics platform for dark store (dark warehouse) operations, featuring AI-powered demand forecasting, route optimization, anomaly detection, and an intelligent chatbot.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Services Description](#services-description)
5. [Quick Start](#quick-start)
6. [Demo Walkthrough](#demo-walkthrough)
7. [API Reference](#api-reference)
8. [Chatbot Usage](#chatbot-usage)
9. [MCP Server Integration](#mcp-server-integration)

---

## Project Overview

### What is a Dark Store?

A dark store is a retail distribution center that exclusively fulfills online orders. Unlike traditional stores, dark stores are not open to the public and are optimized for rapid order picking and fulfillment.

### What Does This Platform Do?

The DarkStore Analytics Platform provides:

- **Real-time KPI Monitoring**: Track orders, fulfillment rates, revenue, and alerts
- **Demand Forecasting**: Predict future demand using multiple ML models (ARIMA, SARIMA, Holt-Winters, Random Forest, Gradient Boosting)
- **Route Optimization**: Optimize picker routes through the warehouse using Nearest Neighbor and 2-opt algorithms
- **Anomaly Detection**: Identify unusual patterns in orders, inventory, and staff performance
- **Product Affinity Analysis**: Discover frequently co-purchased items for better warehouse layout
- **Event Simulation**: Simulate scenarios like flash sales or supply delays
- **AI Chatbot**: Natural language interface powered by Google Gemini
- **MCP Server**: Integration with Claude AI for advanced analytics

### Key Metrics Tracked

| Metric | Description |
|--------|-------------|
| On-Time Rate | Percentage of orders fulfilled within target time |
| Backlog | Number of pending orders |
| Low Stock Items | SKUs below reorder threshold |
| Active Alerts | Critical and high-priority issues |
| Staff Performance | Orders per hour, delay rates |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client Applications                          │
│  (Dashboard, Mobile App, Claude AI, Third-party Integrations)       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
            ┌───────────┐   ┌───────────┐   ┌───────────┐
            │    API    │   │  Chatbot  │   │    MCP    │
            │  Gateway  │   │  (Gemini) │   │  Server   │
            │  :8000    │   │  :8020    │   │  :8010    │
            └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
                  │               │               │
                  └───────────────┼───────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐   ┌───────────────────┐   ┌───────────────────┐
│ Data Service  │   │ Forecaster Service│   │ Route Optimizer   │
│    :8001      │   │      :8002        │   │     :8003         │
└───────────────┘   └───────────────────┘   └───────────────────┘
        │
        ▼
┌───────────────┐   ┌───────────────────┐   ┌───────────────────┐
│   Anomaly     │   │ Affinity Analyzer │   │ Event Simulator   │
│  Detector     │   │      :8005        │   │     :8006         │
│    :8004      │   └───────────────────┘   └───────────────────┘
└───────────────┘
        │
        ▼
┌───────────────┐
│   SQLite DB   │
│ dark_store.db │
└───────────────┘
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend Framework** | FastAPI + Uvicorn |
| **Database** | SQLite (development) |
| **Data Processing** | Pandas, NumPy |
| **ML/Forecasting** | scikit-learn, statsmodels |
| **Chatbot** | LangChain + LangGraph + Google Gemini 2.0 Flash |
| **MCP Server** | FastMCP |
| **HTTP Client** | httpx (async) |
| **Validation** | Pydantic |
| **Containerization** | Docker + docker-compose |

---

## Services Description

### 1. API Gateway (Port 8000)
Central entry point that routes requests to appropriate microservices.

### 2. Data Service (Port 8001)
Provides access to core data: orders, inventory, alerts, staff performance, and KPIs.

### 3. Forecaster Service (Port 8002)
Multi-model demand forecasting engine supporting:
- ARIMA (Auto-Regressive Integrated Moving Average)
- SARIMA (Seasonal ARIMA)
- Holt-Winters Exponential Smoothing
- Random Forest Regressor
- Gradient Boosting Regressor
- Ensemble (weighted average of all models)
- Auto (automatically selects best model)

### 4. Route Optimizer Service (Port 8003)
Optimizes picker routes using:
- **Nearest Neighbor**: Greedy algorithm for quick solutions
- **2-opt**: Local search improvement
- **NN+2opt**: Combined approach (default)

### 5. Anomaly Detector Service (Port 8004)
Detects anomalies using:
- **Isolation Forest**: For order pattern anomalies
- **Z-score Analysis**: For inventory and staff metrics

### 6. Affinity Analyzer Service (Port 8005)
Analyzes product co-purchase patterns:
- Calculates lift, confidence, and support metrics
- Provides co-location recommendations for warehouse layout

### 7. Event Simulator Service (Port 8006)
Simulates operational scenarios:
- **Normal**: Baseline operations
- **Flash Sale**: 3x order volume spike
- **Supply Delay**: Extended fulfillment times

### 8. Chatbot (Port 8020)
LangChain-powered conversational AI with 8 tools for natural language queries.

### 9. MCP Server (Port 8010)
FastMCP server with 12 tools for Claude AI integration.

---

## Quick Start

### Prerequisites
- Python 3.11+
- Google API Key (for Gemini chatbot)

### Installation

```bash
# Clone the repository
cd /Users/ash/Projects/darkstore-analytics-platform

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Starting All Services

```bash
# Option 1: Using the Makefile
make run-all

# Option 2: Start services individually
# Terminal 1 - Data Service
cd services/data-service && uvicorn src.main:app --port 8001 --reload

# Terminal 2 - Forecaster Service
cd services/forecaster-service && uvicorn src.main:app --port 8002 --reload

# Terminal 3 - Route Optimizer Service
cd services/route-optimizer-service && uvicorn src.main:app --port 8003 --reload

# Terminal 4 - Anomaly Detector Service
cd services/anomaly-detector-service && uvicorn src.main:app --port 8004 --reload

# Terminal 5 - Affinity Analyzer Service
cd services/affinity-analyzer-service && uvicorn src.main:app --port 8005 --reload

# Terminal 6 - Event Simulator Service
cd services/event-simulator-service && uvicorn src.main:app --port 8006 --reload

# Terminal 7 - API Gateway
cd services/api-gateway && uvicorn src.main:app --port 8000 --reload

# Terminal 8 - Chatbot (requires GOOGLE_API_KEY)
GOOGLE_API_KEY=your-key-here cd chatbot && uvicorn main:app --port 8020 --reload
```

### Using Docker

```bash
docker-compose up --build
```

---

## Demo Walkthrough

### Step 1: Verify All Services Are Running

```bash
curl http://localhost:8000/health/all
```

Expected output:
```json
{
  "api-gateway": "healthy",
  "data": "healthy",
  "forecast": "healthy",
  "routes": "healthy",
  "anomalies": "healthy",
  "affinity": "healthy",
  "simulate": "healthy"
}
```

### Step 2: Get Dashboard KPIs

```bash
curl http://localhost:8000/api/v1/data/kpis
```

Expected output:
```json
{
  "total_orders_today": 146,
  "total_orders_all": 1000,
  "on_time_rate": 69.5,
  "backlog": 204,
  "avg_fulfillment_minutes": 17.7,
  "total_revenue": 82156.72,
  "revenue_today": 11879.83,
  "low_stock_count": 20,
  "total_skus": 150,
  "stock_health_rate": 86.7,
  "active_alerts": 119,
  "critical_alerts": 67
}
```

### Step 3: Demand Forecasting Demo

```bash
# Forecast demand for SKU01000 for 14 days
curl -X POST http://localhost:8000/api/v1/forecast/sku \
  -H "Content-Type: application/json" \
  -d '{"sku_id": "SKU01000", "forecast_days": 14, "mode": "auto"}'
```

### Step 4: Route Optimization Demo

```bash
# Optimize a picking route for 5 locations
curl -X POST http://localhost:8000/api/v1/routes/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "pick_list": ["A05-3", "B12-2", "C03-1", "D08-4", "E15-2"],
    "method": "nn+2opt"
  }'
```

Expected output shows optimized route with improvement percentage:
```json
{
  "route": ["ENTRANCE", "A05-3", "C03-1", "B12-2", "D08-4", "E15-2", "PACKING"],
  "distance": 185.0,
  "naive_distance": 330.0,
  "improvement_percent": 43.9,
  "estimated_time_minutes": 4.7,
  "num_stops": 5
}
```

### Step 5: Anomaly Detection Demo

```bash
# Detect order anomalies
curl -X POST http://localhost:8000/api/v1/anomalies/orders \
  -H "Content-Type: application/json" \
  -d '{"contamination": 0.05}'
```

### Step 6: Product Affinity Demo

```bash
# Get top 10 frequently co-purchased product pairs
curl "http://localhost:8000/api/v1/affinity/pairs?top_n=10&min_lift=1.0"
```

### Step 7: Chatbot Demo

```bash
# Ask the chatbot a question
curl -X POST http://localhost:8020/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is our on-time delivery rate and how many items need restocking?", "session_id": "demo"}'
```

Example response:
```json
{
  "response": "The current on-time rate is 69.5%. There are 20 items that need restocking, with the most critical being Fresho Fresh Bananas (0 in stock) and Farm Fresh Fresh Tomatoes (0 in stock).",
  "session_id": "demo"
}
```

### Step 8: Simulation Demo

```bash
# Simulate a flash sale scenario
curl -X POST http://localhost:8000/api/v1/simulate/scenario \
  -H "Content-Type: application/json" \
  -d '{"scenario_type": "flash_sale", "duration_hours": 2}'
```

---

## API Reference

### Data Service Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/data/kpis` | Get summary KPIs |
| GET | `/api/v1/data/orders?limit=100&offset=0` | Get orders list |
| GET | `/api/v1/data/inventory?limit=100&offset=0` | Get inventory list |
| GET | `/api/v1/data/inventory/low-stock?limit=20` | Get low stock items |
| GET | `/api/v1/data/alerts?limit=50` | Get active alerts |
| GET | `/api/v1/data/staff/performance` | Get staff metrics |

### Forecaster Service Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/forecast/sku` | Forecast single SKU demand |
| POST | `/api/v1/forecast/compare` | Compare forecast models |

### Route Optimizer Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/routes/optimize` | Optimize picking route |
| POST | `/api/v1/routes/batch` | Batch route optimization |

### Anomaly Detector Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/anomalies/orders` | Detect order anomalies |
| GET | `/api/v1/anomalies/inventory` | Detect inventory anomalies |
| GET | `/api/v1/anomalies/staff` | Detect staff anomalies |

### Affinity Analyzer Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/affinity/pairs` | Get co-purchased pairs |
| GET | `/api/v1/affinity/recommendations` | Get placement suggestions |

### Event Simulator Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/simulate/scenario` | Run simulation |

---

## Chatbot Usage

The chatbot understands natural language queries about warehouse operations.

### Example Queries

| Query | What it does |
|-------|--------------|
| "What's our on-time rate?" | Fetches KPIs |
| "Show me low stock items" | Gets inventory needing restock |
| "Forecast demand for SKU01000" | Runs demand prediction |
| "Optimize route for A05-3, B12-2, C03-1" | Optimizes picking path |
| "Are there any anomalies?" | Runs anomaly detection |
| "What products are bought together?" | Shows product affinities |
| "Show me active alerts" | Lists current alerts |
| "How is staff performing?" | Shows staff metrics |

### API Usage

```bash
# Start a conversation
curl -X POST http://localhost:8020/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Your question here", "session_id": "unique-session-id"}'

# Clear conversation history
curl -X DELETE http://localhost:8020/api/v1/chat/unique-session-id
```

---

## MCP Server Integration

The MCP (Model Context Protocol) server provides 12 tools for Claude AI integration.

### Available Tools

1. `forecast_demand` - Forecast SKU demand
2. `compare_forecast_models` - Compare all forecast models
3. `optimize_picking_route` - Optimize picker route
4. `batch_optimize_routes` - Batch route optimization
5. `detect_order_anomalies` - Find order anomalies
6. `detect_inventory_anomalies` - Find inventory issues
7. `detect_staff_anomalies` - Find staff performance issues
8. `get_product_affinities` - Get co-purchased items
9. `get_colocation_recommendations` - Get placement suggestions
10. `run_simulation` - Run scenario simulation
11. `get_dashboard_kpis` - Get all KPIs
12. `get_low_stock_items` - Get restock needs

### Starting the MCP Server

```bash
cd mcp-server
uvicorn main:app --port 8010
```

### Claude Code Integration

Add to your Claude Code MCP settings:
```json
{
  "mcpServers": {
    "darkstore": {
      "command": "uvicorn",
      "args": ["main:app", "--port", "8010"],
      "cwd": "/path/to/darkstore-analytics-platform/mcp-server"
    }
  }
}
```

---

## Project Structure

```
darkstore-analytics-platform/
├── services/
│   ├── api-gateway/           # FastAPI gateway (port 8000)
│   │   └── src/main.py
│   ├── data-service/          # Data access layer (port 8001)
│   │   └── src/
│   │       ├── main.py
│   │       └── database.py
│   ├── forecaster-service/    # Demand forecasting (port 8002)
│   │   └── src/
│   │       ├── main.py
│   │       └── forecaster.py
│   ├── route-optimizer-service/   # Route optimization (port 8003)
│   │   └── src/
│   │       ├── main.py
│   │       └── optimizer.py
│   ├── anomaly-detector-service/  # Anomaly detection (port 8004)
│   │   └── src/
│   │       ├── main.py
│   │       └── detector.py
│   ├── affinity-analyzer-service/ # Product affinity (port 8005)
│   │   └── src/
│   │       ├── main.py
│   │       └── analyzer.py
│   └── event-simulator-service/   # Event simulation (port 8006)
│       └── src/
│           ├── main.py
│           └── simulator.py
├── mcp-server/                # FastMCP server (port 8010)
│   └── main.py
├── chatbot/                   # LangChain chatbot (port 8020)
│   └── main.py
├── shared/                    # Shared Pydantic models
│   └── models/
│       ├── data.py
│       ├── forecast.py
│       ├── routes.py
│       ├── anomalies.py
│       └── affinity.py
├── data/                      # SQLite database
│   └── dark_store.db
├── docker-compose.yml
├── requirements.txt
├── Makefile
└── PROJECT_DOCUMENTATION.md
```

---

## Data Model

### Orders Table
- `order_id`: Unique order identifier
- `timestamp`: Order creation time
- `num_items`: Number of unique SKUs
- `total_quantity`: Total items ordered
- `total_value`: Order value in currency
- `status`: Pending, Picking, Packing, Delivered
- `assigned_staff`: Staff ID handling order
- `fulfillment_time_minutes`: Time to fulfill
- `is_delayed`: Whether order exceeded target time
- `items`: JSON array of SKU/quantity pairs

### Inventory Table
- `sku_id`: SKU identifier (SKU01000-SKU01149)
- `product_name`: Product description
- `category`: Product category
- `current_stock`: Units in stock
- `reorder_threshold`: Minimum stock level
- `shelf_location`: Warehouse location (e.g., A05-3)
- `unit_price`: Price per unit
- `expiry_date`: Expiration date (if applicable)
- `demand_rate`: Low/Medium/High

### Alerts Table
- `alert_id`: Alert identifier
- `alert_type`: Low Stock, Delay, etc.
- `severity`: Critical, High, Medium, Low
- `status`: Open, Acknowledged, Resolved
- `message`: Alert description
- `related_sku`: Associated SKU (if applicable)
- `related_order`: Associated order (if applicable)

### Staff Table
- `staff_id`: Staff identifier
- `name`: Staff name
- `role`: Picker, Packer, etc.

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| Total SKUs | 150 |
| Total Orders | 1,000 |
| Average Fulfillment Time | 17.7 minutes |
| On-Time Rate | 69.5% |
| Low Stock Items | 20 |
| Active Alerts | 119 |

---

## Troubleshooting

### Service Not Starting
```bash
# Check if port is in use
lsof -i :8000

# Kill process on port
kill -9 $(lsof -t -i :8000)
```

### Database Not Found
```bash
# Verify database exists
ls -la data/dark_store.db
```

### Chatbot Not Responding
```bash
# Verify GOOGLE_API_KEY is set
echo $GOOGLE_API_KEY

# Check chatbot health
curl http://localhost:8020/health
```

---

## License

This project is for demonstration and educational purposes.

---

## Author

Built with FastAPI, LangChain, and love for warehouse operations optimization.
