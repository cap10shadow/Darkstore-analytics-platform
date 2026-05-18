"""LangChain-powered AI Chatbot for DarkStore Analytics Platform."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import httpx
import os
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

app = FastAPI(
    title="DarkStore AI Chatbot",
    description="LangChain-powered chatbot for darkstore analytics (Gemini)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== API Client ====================

def sync_api_call(method: str, path: str, json_data: dict = None, params: dict = None) -> str:
    """Synchronous API call for LangChain tools."""
    url = f"{GATEWAY_URL}{path}"
    try:
        with httpx.Client(timeout=60.0) as client:
            if method == "GET":
                response = client.get(url, params=params)
            else:
                response = client.post(url, json=json_data, params=params)

            if response.status_code >= 400:
                return json.dumps({"error": f"API error: {response.status_code}"})

            return json.dumps(response.json(), indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ==================== LangChain Tools ====================

@tool
def get_kpis() -> str:
    """Get summary KPIs including order counts, on-time rate, revenue, and alerts."""
    return sync_api_call("GET", "/api/v1/data/kpis")


@tool
def get_low_stock(limit: int = 20) -> str:
    """Get items with low stock levels and reorder recommendations.

    Args:
        limit: Maximum number of items to return
    """
    return sync_api_call("GET", "/api/v1/data/inventory/low-stock", params={"limit": limit})


@tool
def forecast_demand(sku_id: str, forecast_days: int = 14) -> str:
    """Forecast demand for a specific SKU.

    Args:
        sku_id: The SKU identifier (e.g., 'SKU01000')
        forecast_days: Number of days to forecast
    """
    return sync_api_call("POST", "/api/v1/forecast/sku", json_data={
        "sku_id": sku_id,
        "forecast_days": forecast_days,
        "mode": "auto"
    })


@tool
def optimize_route(pick_list: str) -> str:
    """Optimize the picking route for shelf locations.

    Args:
        pick_list: Comma-separated shelf locations (e.g., 'A05-3,B12-2,C03-1')
    """
    locations = [loc.strip() for loc in pick_list.split(",")]
    return sync_api_call("POST", "/api/v1/routes/optimize", json_data={
        "pick_list": locations,
        "method": "nn+2opt"
    })


@tool
def detect_anomalies(anomaly_type: str = "orders") -> str:
    """Detect anomalies in operations.

    Args:
        anomaly_type: Type of anomalies to detect - 'orders', 'inventory', or 'staff'
    """
    if anomaly_type == "orders":
        return sync_api_call("POST", "/api/v1/anomalies/orders", json_data={"contamination": 0.05})
    elif anomaly_type == "inventory":
        return sync_api_call("GET", "/api/v1/anomalies/inventory")
    elif anomaly_type == "staff":
        return sync_api_call("GET", "/api/v1/anomalies/staff")
    else:
        return json.dumps({"error": "Invalid anomaly type. Use 'orders', 'inventory', or 'staff'"})


@tool
def get_product_pairs(top_n: int = 10) -> str:
    """Get frequently co-purchased product pairs.

    Args:
        top_n: Number of top pairs to return
    """
    return sync_api_call("GET", "/api/v1/affinity/pairs", params={"top_n": top_n, "min_lift": 1.0})


@tool
def get_alerts(limit: int = 20) -> str:
    """Get active alerts sorted by severity.

    Args:
        limit: Maximum number of alerts to return
    """
    return sync_api_call("GET", "/api/v1/data/alerts", params={"limit": limit})


@tool
def get_staff_performance() -> str:
    """Get staff performance metrics including orders completed, fulfillment times, and delay rates."""
    return sync_api_call("GET", "/api/v1/data/staff/performance")


# Tool list
tools = [
    get_kpis,
    get_low_stock,
    forecast_demand,
    optimize_route,
    detect_anomalies,
    get_product_pairs,
    get_alerts,
    get_staff_performance,
]


# ==================== Agent Setup ====================

SYSTEM_PROMPT = """You are an AI assistant for a DarkStore (dark warehouse) operations platform.
You help warehouse managers and analysts with:

1. **Operational Monitoring**: KPIs, alerts, and real-time status
2. **Demand Forecasting**: Predict future demand for SKUs
3. **Route Optimization**: Optimize picking routes in the warehouse
4. **Anomaly Detection**: Identify unusual patterns in orders, inventory, or staff
5. **Product Affinity**: Find frequently co-purchased items
6. **Inventory Management**: Track low stock and reorder needs

When answering:
- Be concise but informative
- Use actual data from the tools when available
- Provide actionable insights
- If data shows issues (delays, low stock, anomalies), highlight them
- Format numbers nicely (e.g., percentages, currency)

Available SKU format: SKU01000 to SKU01149
Shelf location format: A05-3 (Aisle A, Bay 05, Shelf 3)
"""

def create_agent():
    """Create the LangGraph agent with Gemini."""
    if not GOOGLE_API_KEY:
        return None

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=GOOGLE_API_KEY
    )

    agent = create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)
    return agent


# Global agent instance
agent_graph = None

# Conversation history storage (in-memory, per-session)
conversation_histories = {}


# ==================== API Endpoints ====================

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: str = Field(default="default", description="Session ID for conversation history")


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.on_event("startup")
async def startup():
    global agent_graph
    agent_graph = create_agent()
    if agent_graph is None:
        print("WARNING: GOOGLE_API_KEY not set. Chatbot will not function.")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "chatbot",
        "agent_ready": agent_graph is not None
    }


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the chatbot and get a response."""
    if agent_graph is None:
        raise HTTPException(
            status_code=503,
            detail="Chatbot not initialized. Please set GOOGLE_API_KEY environment variable."
        )

    # Get or create conversation history
    if request.session_id not in conversation_histories:
        conversation_histories[request.session_id] = []

    chat_history = conversation_histories[request.session_id]

    try:
        # Build messages with history
        messages = chat_history + [HumanMessage(content=request.message)]

        # Run the agent
        result = agent_graph.invoke({"messages": messages})

        # Extract response
        response_text = result["messages"][-1].content

        # Update conversation history (keep last 10 exchanges)
        chat_history.append(HumanMessage(content=request.message))
        chat_history.append(AIMessage(content=response_text))
        if len(chat_history) > 20:
            chat_history = chat_history[-20:]
        conversation_histories[request.session_id] = chat_history

        return ChatResponse(response=response_text, session_id=request.session_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.delete("/api/v1/chat/{session_id}")
async def clear_history(session_id: str):
    """Clear conversation history for a session."""
    if session_id in conversation_histories:
        del conversation_histories[session_id]
    return {"message": f"History cleared for session {session_id}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)
