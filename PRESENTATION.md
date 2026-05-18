# DarkStore Analytics Platform
## An AI-Powered Microservices Architecture for Warehouse Operations

---

# What is a Dark Store?

## Definition
A dark store is a retail distribution center that exclusively fulfills online orders. Unlike traditional retail stores, dark stores are not open to the public.

## Characteristics
- Optimized for rapid order picking and packing
- No customer foot traffic
- Layout designed for operational efficiency
- Focus on speed-to-delivery metrics

## Use Cases
- Grocery delivery (10-30 minute delivery)
- Quick commerce (q-commerce)
- Last-mile fulfillment centers

---

# The Business Problem

## Challenges in Dark Store Operations

| Challenge | Impact |
|-----------|--------|
| Inefficient Picking Routes | Workers walk unnecessary distances |
| Reactive Inventory Management | Stockouts discovered too late |
| No Predictive Capabilities | Cannot anticipate demand spikes |
| Manual Anomaly Detection | Issues go unnoticed |
| Siloed Information | Data trapped in separate systems |
| Limited Scalability | Systems cannot grow with business |

---

# Solution Overview

## DarkStore Analytics Platform

A comprehensive analytics solution that provides:

- Real-time operational monitoring
- AI-powered demand forecasting
- Intelligent route optimization
- Automated anomaly detection
- Product affinity analysis
- Scenario simulation capabilities
- Natural language AI interface

---

# Architecture Philosophy

## Microservices Architecture

### Why Microservices?

| Benefit | Description |
|---------|-------------|
| **Scalability** | Scale individual services based on demand |
| **Resilience** | Failure in one service doesn't crash the system |
| **Flexibility** | Use different technologies per service |
| **Maintainability** | Smaller codebases are easier to manage |
| **Deployment** | Deploy services independently |

---

# System Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│              Client Applications                 │
│    (Dashboards, Mobile Apps, AI Assistants)     │
└─────────────────────────────────────────────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │   API    │  │ Chatbot  │  │   MCP    │
    │ Gateway  │  │ Service  │  │  Server  │
    └────┬─────┘  └──────────┘  └──────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│            Backend Microservices                 │
├─────────┬─────────┬─────────┬─────────┬────────┤
│  Data   │Forecast │ Route   │ Anomaly │Affinity│
│ Service │ Service │Optimizer│ Detector│Analyzer│
└─────────┴─────────┴─────────┴─────────┴────────┘
                        │
                        ▼
              ┌─────────────────┐
              │    Database     │
              └─────────────────┘
```

---

# Component Overview

## 9 Core Components

| # | Component | Purpose |
|---|-----------|---------|
| 1 | API Gateway | Central request routing |
| 2 | Data Service | Core data access layer |
| 3 | Forecaster Service | Demand prediction |
| 4 | Route Optimizer Service | Picking path optimization |
| 5 | Anomaly Detector Service | Pattern anomaly detection |
| 6 | Affinity Analyzer Service | Product relationship analysis |
| 7 | Event Simulator Service | Scenario modeling |
| 8 | AI Chatbot | Natural language interface |
| 9 | MCP Server | AI assistant integration |

---

# API Gateway

## The Central Entry Point

### Purpose
Routes all incoming requests to the appropriate microservice

### Responsibilities
- Request routing and load distribution
- Cross-Origin Resource Sharing (CORS) handling
- Health check aggregation across all services
- Unified API endpoint for clients

### How It Works
```
Client Request → API Gateway → Appropriate Microservice → Response
```

---

# Data Service

## The Data Access Layer

### Purpose
Provides unified access to all operational data

### Data Entities
- **Orders** — Order details, status, fulfillment times
- **Inventory** — Stock levels, locations, expiry dates
- **Alerts** — System warnings and notifications
- **Staff** — Employee information and assignments

### Key Outputs
- Summary KPIs (Key Performance Indicators)
- Low stock item identification
- Active alert listings
- Staff performance metrics

---

# Data Model

## Core Database Entities

### Orders Table
- Order ID, timestamp, items list
- Total value, quantity
- Status (Pending → Picking → Packing → Delivered)
- Assigned staff, fulfillment time
- Delay flag

### Inventory Table
- SKU ID, product name, category
- Current stock level
- Reorder threshold
- Shelf location (e.g., A05-3)
- Unit price, expiry date

### Alerts Table
- Alert type and severity
- Related SKU or order
- Status (Open/Acknowledged/Resolved)

---

# Key Performance Indicators (KPIs)

## Metrics Tracked by the Platform

| KPI | Description |
|-----|-------------|
| **Total Orders** | Orders received (today / all-time) |
| **On-Time Rate** | Percentage of orders meeting target time |
| **Backlog** | Pending orders awaiting fulfillment |
| **Average Fulfillment Time** | Mean time from order to dispatch |
| **Revenue** | Total and daily revenue figures |
| **Low Stock Count** | Items below reorder threshold |
| **Stock Health Rate** | Percentage of healthy inventory |
| **Active Alerts** | Open issues requiring attention |
| **Critical Alerts** | High-priority problems |

---

# Forecaster Service

## Demand Prediction Engine

### Purpose
Predicts future demand for each SKU to enable proactive inventory management

### Why Forecasting Matters
- Prevent stockouts before they happen
- Optimize reorder quantities
- Plan for seasonal variations
- Reduce holding costs

---

# Forecasting Models

## Multi-Model Approach

| Model | Type | Best For |
|-------|------|----------|
| **ARIMA** | Statistical | Stable demand patterns |
| **SARIMA** | Statistical | Seasonal patterns |
| **Holt-Winters** | Statistical | Trend + seasonality |
| **Random Forest** | Machine Learning | Complex patterns |
| **Gradient Boosting** | Machine Learning | High accuracy needs |
| **Ensemble** | Combined | Balanced predictions |

**Auto Mode:** Automatically selects the best-performing model based on historical accuracy

---

# Forecasting Process

## How Demand Forecasting Works

```
Step 1: Collect Historical Data
           ↓
Step 2: Analyze Demand Patterns
           ↓
Step 3: Train Multiple Models
           ↓
Step 4: Generate Predictions
           ↓
Step 5: Calculate Reorder Recommendations
           ↓
Step 6: Output Forecast with Confidence Intervals
```

### Output Includes
- Daily demand predictions
- Recommended reorder quantity
- Estimated reorder cost
- Model confidence metrics

---

# Route Optimizer Service

## Picking Path Optimization

### Purpose
Calculates the most efficient route for warehouse pickers to collect items

### The Problem
- Warehouses have thousands of shelf locations
- Pickers receive lists of items to collect
- Unoptimized routes waste time and energy
- Manual planning is impractical at scale

---

# Warehouse Layout Model

## How the Warehouse is Represented

### Location Format: `A05-3`
- **A** = Aisle letter (A-Z)
- **05** = Bay number (01-20)
- **3** = Shelf level (1-5)

### Coordinate System
- Each location mapped to X,Y coordinates
- Distance calculated using Manhattan distance
- Special locations: ENTRANCE, PACKING

---

# Route Optimization Algorithms

## Two-Stage Optimization

### Stage 1: Nearest Neighbor Algorithm
- Start at entrance
- Always move to closest unvisited location
- Greedy approach for quick initial solution

### Stage 2: 2-opt Improvement
- Take the initial route
- Try swapping pairs of edges
- Keep improvements, discard worse solutions
- Repeat until no improvement found

**Result:** Routes typically 30-45% shorter than naive ordering

---

# Route Optimization Visualization

## Before vs After Optimization

```
Naive Route:                    Optimized Route:
ENTRANCE                        ENTRANCE
    ↓                               ↓
   E15  (far)                      A05  (near)
    ↓                               ↓
   A05  (backtrack)                B12  (logical)
    ↓                               ↓
   D08  (far again)                C03  (sequential)
    ↓                               ↓
   B12                             D08
    ↓                               ↓
   C03                             E15
    ↓                               ↓
PACKING                         PACKING

Distance: 330m                  Distance: 185m
                                Improvement: 44%
```

---

# Anomaly Detector Service

## Automated Pattern Detection

### Purpose
Identifies unusual patterns that may indicate problems or opportunities

### Three Detection Areas
1. Order Anomalies
2. Inventory Anomalies
3. Staff Performance Anomalies

---

# Anomaly Detection Methods

## Machine Learning Approaches

### Isolation Forest (for Orders)
- Unsupervised learning algorithm
- Isolates anomalies by random partitioning
- Effective for high-dimensional data
- Detects unusual order patterns

### Z-Score Analysis (for Inventory & Staff)
- Statistical method
- Measures standard deviations from mean
- Flags values beyond threshold
- Simple and interpretable

---

# Types of Anomalies Detected

## What the System Catches

| Category | Anomaly Type | Example |
|----------|--------------|---------|
| **Orders** | Unusual value | Order 10x normal size |
| **Orders** | Strange timing | Orders at unusual hours |
| **Orders** | Fulfillment issues | Extremely long processing |
| **Inventory** | Stock discrepancy | Negative stock values |
| **Inventory** | Unusual movement | Sudden stock changes |
| **Staff** | Performance outlier | Unusually slow fulfillment |
| **Staff** | Delay patterns | High delay rate |

---

# Affinity Analyzer Service

## Product Relationship Analysis

### Purpose
Discovers which products are frequently purchased together

### Business Applications
- Optimize warehouse layout (place related items nearby)
- Bundle recommendations
- Cross-selling opportunities
- Demand correlation understanding

---

# Affinity Metrics

## How Product Relationships are Measured

| Metric | Definition | Use |
|--------|------------|-----|
| **Support** | How often items appear together | Frequency measure |
| **Confidence** | P(B\|A) - If A bought, likelihood of B | Prediction strength |
| **Lift** | How much more likely than random | Relationship strength |

### Example
- Bananas and Milk have Lift = 2.5
- Means they're bought together 2.5x more often than expected by chance

---

# Co-location Recommendations

## Warehouse Layout Optimization

### The Concept
If products are frequently bought together, placing them near each other:
- Reduces picker travel time
- Speeds up order fulfillment
- Improves operational efficiency

### Output
- Product pairs with high affinity scores
- Current shelf locations of each product
- Distance between current locations
- Recommendation to co-locate

---

# Event Simulator Service

## Scenario Modeling

### Purpose
Simulates different operational scenarios to test system resilience and plan for events

### Available Scenarios

| Scenario | Description |
|----------|-------------|
| **Normal** | Baseline operations |
| **Flash Sale** | 3x order volume spike |
| **Supply Delay** | Extended fulfillment times |

---

# Simulation Process

## How Simulation Works

```
Step 1: Define Scenario Parameters
        - Type (normal/flash_sale/supply_delay)
        - Duration (hours)

Step 2: Generate Synthetic Events
        - Order arrivals
        - Processing times
        - Staff assignments

Step 3: Apply Scenario Modifiers
        - Adjust volumes and timings

Step 4: Output Event Stream
        - Timestamped events
        - Metrics and summaries
```

### Use Cases
- Capacity planning
- Staff scheduling
- System stress testing

---

# AI Chatbot

## Natural Language Interface

### Purpose
Allows users to query the system using everyday language instead of technical interfaces

### Powered By
- **LangChain** — AI application framework
- **LangGraph** — Agent orchestration
- **Google Gemini 2.0 Flash** — Large Language Model

---

# Chatbot Architecture

## How the Chatbot Works

```
User Query (Natural Language)
           ↓
    LangChain Agent
           ↓
    Tool Selection
           ↓
    API Call to Services
           ↓
    Response Processing
           ↓
    Natural Language Answer
```

**Key Feature:** Conversation memory maintains context across multiple exchanges

---

# Chatbot Tools

## 8 Available Tools

| Tool | Function |
|------|----------|
| `get_kpis` | Retrieve summary KPIs |
| `get_low_stock` | Get items needing restock |
| `forecast_demand` | Predict SKU demand |
| `optimize_route` | Calculate optimal picking path |
| `detect_anomalies` | Find unusual patterns |
| `get_product_pairs` | Get co-purchased items |
| `get_alerts` | Retrieve active alerts |
| `get_staff_performance` | Get staff metrics |

---

# Example Chatbot Interactions

## Natural Language Queries

| User Says | System Does |
|-----------|-------------|
| "What's our on-time rate?" | Calls get_kpis, extracts on-time rate |
| "Show me low stock items" | Calls get_low_stock, formats list |
| "Forecast demand for SKU01000" | Calls forecast_demand with SKU |
| "Optimize route for A05, B12, C03" | Calls optimize_route, shows path |
| "Are there any anomalies?" | Calls detect_anomalies, summarizes |
| "Which products are bought together?" | Calls get_product_pairs, lists top pairs |

---

# MCP Server

## Model Context Protocol Integration

### What is MCP?
Model Context Protocol — a standard for AI assistants to interact with external tools and data sources

### Purpose
Enables Claude AI to directly access and analyze dark store data

---

# MCP Server Tools

## 12 Tools for AI Integration

| # | Tool | Purpose |
|---|------|---------|
| 1 | `forecast_demand` | SKU demand prediction |
| 2 | `compare_forecast_models` | Model comparison |
| 3 | `optimize_picking_route` | Route optimization |
| 4 | `batch_optimize_routes` | Multiple route optimization |
| 5 | `detect_order_anomalies` | Order pattern analysis |
| 6 | `detect_inventory_anomalies` | Stock anomaly detection |
| 7 | `detect_staff_anomalies` | Staff performance analysis |
| 8 | `get_product_affinities` | Co-purchase analysis |
| 9 | `get_colocation_recommendations` | Layout suggestions |
| 10 | `run_simulation` | Scenario simulation |
| 11 | `get_dashboard_kpis` | KPI retrieval |
| 12 | `get_low_stock_items` | Low stock identification |

---

# MCP Resources

## Data Schemas for AI Context

| Resource | Content |
|----------|---------|
| `schema://orders` | Order data structure |
| `schema://inventory` | Inventory data structure |
| `config://warehouse` | Warehouse layout configuration |

**Purpose:** Provides AI with understanding of data formats for better analysis

---

# Technology Stack

## Technologies Used

| Layer | Technology |
|-------|------------|
| **Backend Framework** | FastAPI |
| **Server** | Uvicorn (ASGI) |
| **Database** | SQLite |
| **Data Processing** | Pandas, NumPy |
| **Machine Learning** | scikit-learn |
| **Statistical Models** | statsmodels |
| **AI Chatbot** | LangChain, LangGraph |
| **LLM** | Google Gemini 2.0 Flash |
| **MCP Server** | FastMCP |
| **Data Validation** | Pydantic |
| **HTTP Client** | httpx |
| **Containerization** | Docker |

---

# Why FastAPI?

## Backend Framework Choice

### Advantages
- **High Performance** — One of the fastest Python frameworks
- **Automatic Documentation** — Swagger UI generated automatically
- **Type Safety** — Pydantic integration for validation
- **Async Support** — Native asynchronous request handling
- **Easy to Learn** — Clean, intuitive syntax

---

# Why Pydantic?

## Data Validation Layer

### Purpose
Ensures data integrity throughout the system

### Benefits
- Automatic request/response validation
- Clear data schemas
- Type hints for IDE support
- Serialization to JSON
- Error messages for invalid data

### Example Models
- `Order`, `InventoryItem`, `Alert`
- `ForecastRequest`, `ForecastResponse`
- `RouteOptimizationRequest`, `RouteResult`

---

# Why LangChain?

## AI Application Framework

### Purpose
Simplifies building applications powered by Large Language Models

### Components Used
- **Tools** — Define functions the AI can call
- **Agents** — Autonomous decision-making
- **Memory** — Conversation history
- **LangGraph** — Agent orchestration

**Benefit:** Abstracts complexity of LLM integration

---

# Data Flow - KPI Request

## Example: Getting Dashboard KPIs

```
1. Client sends GET /api/v1/data/kpis
           ↓
2. API Gateway receives request
           ↓
3. Request forwarded to Data Service
           ↓
4. Data Service queries database
           ↓
5. Calculations performed (on-time rate, etc.)
           ↓
6. Response formatted as JSON
           ↓
7. Returned through API Gateway to client
```

---

# Data Flow - Forecast Request

## Example: Demand Forecasting

```
1. Client sends POST /api/v1/forecast/sku
   Body: { sku_id: "SKU01000", forecast_days: 14 }
           ↓
2. API Gateway routes to Forecaster Service
           ↓
3. Forecaster retrieves historical order data
           ↓
4. Multiple models trained on data
           ↓
5. Best model selected (or ensemble used)
           ↓
6. Predictions generated for next 14 days
           ↓
7. Reorder recommendations calculated
           ↓
8. Response returned with forecast + recommendations
```

---

# Data Flow - Chatbot Query

## Example: Natural Language Query

```
1. User: "What items need restocking?"
           ↓
2. Chatbot receives message
           ↓
3. LangChain Agent analyzes intent
           ↓
4. Agent selects "get_low_stock" tool
           ↓
5. Tool calls Data Service API
           ↓
6. Low stock items retrieved
           ↓
7. Agent formats response in natural language
           ↓
8. Response: "There are 20 items below reorder
   threshold. The most critical are..."
```

---

# Deployment Architecture

## Containerized Deployment

```
┌─────────────────────────────────────────────┐
│              Docker Compose                  │
├─────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ Gateway │ │  Data   │ │Forecast │       │
│  │ :8000   │ │ :8001   │ │ :8002   │       │
│  └─────────┘ └─────────┘ └─────────┘       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ Routes  │ │ Anomaly │ │Affinity │       │
│  │ :8003   │ │ :8004   │ │ :8005   │       │
│  └─────────┘ └─────────┘ └─────────┘       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │Simulate │ │ Chatbot │ │   MCP   │       │
│  │ :8006   │ │ :8020   │ │ :8010   │       │
│  └─────────┘ └─────────┘ └─────────┘       │
├─────────────────────────────────────────────┤
│              Internal Network                │
└─────────────────────────────────────────────┘
```

---

# Service Communication

## Inter-Service Communication

### Pattern: Synchronous HTTP/REST

### Flow
- API Gateway acts as entry point
- Services communicate via HTTP requests
- JSON used for data exchange
- Each service has health check endpoint

### Benefits
- Simple and well-understood
- Easy debugging
- Standard tooling available

---

# Project Structure

## Codebase Organization

```
darkstore-analytics-platform/
│
├── services/
│   ├── api-gateway/
│   ├── data-service/
│   ├── forecaster-service/
│   ├── route-optimizer-service/
│   ├── anomaly-detector-service/
│   ├── affinity-analyzer-service/
│   └── event-simulator-service/
│
├── chatbot/
├── mcp-server/
├── shared/          (Common models)
├── data/            (Database)
└── docker-compose.yml
```

---

# Shared Components

## Common Library

### Purpose
Defines shared data models used across services

### Models Defined
- Data models (Order, Inventory, Alert, Staff)
- Forecast models (Request, Response, Comparison)
- Route models (Optimization request, Result)
- Anomaly models (Detection results)
- Affinity models (Product pairs, Recommendations)

**Benefit:** Ensures consistency across all services

---

# Security Considerations

## Platform Security

| Area | Approach |
|------|----------|
| **API Access** | CORS configuration |
| **Input Validation** | Pydantic models validate all inputs |
| **Error Handling** | Graceful error responses |
| **Service Isolation** | Each service runs independently |
| **Environment Variables** | Secrets stored in environment |

---

# Scalability

## How the Platform Scales

### Horizontal Scaling
- Each microservice can be scaled independently
- Add more instances of busy services
- Load balancer distributes requests

### Vertical Scaling
- Increase resources for specific services
- Forecaster may need more CPU for ML
- Data Service may need more memory

### Database Scaling
- SQLite for development
- PostgreSQL for production
- Database replication for read scaling

---

# Benefits Summary

## What the Platform Delivers

| Benefit | Description |
|---------|-------------|
| **Operational Visibility** | Real-time KPIs and alerts |
| **Predictive Capability** | Demand forecasting prevents stockouts |
| **Efficiency Gains** | Optimized routes save 30-45% travel |
| **Proactive Detection** | Anomalies caught automatically |
| **Better Layout** | Affinity analysis improves warehouse design |
| **Accessible Insights** | Natural language queries for everyone |
| **AI Integration** | Claude AI can analyze operations |
| **Future Ready** | Microservices architecture scales |

---

# Use Cases

## Who Uses What

| User Role | Primary Features |
|-----------|------------------|
| **Warehouse Manager** | KPIs, Alerts, Staff Performance |
| **Inventory Planner** | Forecasting, Low Stock, Reorder Recommendations |
| **Operations Lead** | Route Optimization, Anomaly Detection |
| **Layout Designer** | Affinity Analysis, Co-location Recommendations |
| **Capacity Planner** | Event Simulation |
| **Executive** | Chatbot for quick insights |

---

# Summary

## DarkStore Analytics Platform

A comprehensive solution transforming dark store operations through:

- **Microservices Architecture** — Scalable, maintainable, resilient
- **AI-Powered Analytics** — Forecasting, optimization, detection
- **Natural Language Interface** — Accessible to all users
- **Real-time Insights** — KPIs, alerts, and recommendations
- **Modern Technology Stack** — FastAPI, LangChain, Docker

---

# Thank You

## Platform Components

- 7 Backend Microservices
- 1 AI Chatbot (Gemini)
- 1 MCP Server (Claude Integration)
- 12 MCP Tools
- 8 Chatbot Tools
- 15+ API Endpoints

---
