"""FastMCP Server for DarkStore Analytics Platform.

This MCP server provides Claude with tools to interact with the DarkStore
microservices platform for analytics, forecasting, and operational insights.
"""
from fastmcp import FastMCP
import httpx
import os
import json

# API Gateway URL
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")

mcp = FastMCP("DarkStoreAnalytics")


async def api_call(method: str, path: str, json_data: dict = None, params: dict = None) -> dict:
    """Make an API call to the gateway."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        url = f"{GATEWAY_URL}{path}"
        try:
            if method == "GET":
                response = await client.get(url, params=params)
            else:
                response = await client.post(url, json=json_data, params=params)

            if response.status_code >= 400:
                return {"error": f"API error: {response.status_code}", "detail": response.text}

            return response.json()
        except httpx.ConnectError:
            return {"error": "Service unavailable. Make sure the API gateway is running."}
        except Exception as e:
            return {"error": str(e)}


# ==================== FORECASTING TOOLS ====================

@mcp.tool()
async def forecast_demand(sku_id: str, forecast_days: int = 14, mode: str = "auto") -> dict:
    """Forecast demand for a specific SKU.

    Args:
        sku_id: The SKU identifier (e.g., 'SKU-0001')
        forecast_days: Number of days to forecast (1-90)
        mode: Forecasting mode - 'auto' selects best model, 'ensemble' uses all models
    """
    return await api_call("POST", "/api/v1/forecast/sku", json_data={
        "sku_id": sku_id,
        "forecast_days": forecast_days,
        "mode": mode
    })


@mcp.tool()
async def compare_forecast_models(sku_id: str, forecast_days: int = 14) -> dict:
    """Compare all available forecasting models for a SKU.

    Args:
        sku_id: The SKU identifier
        forecast_days: Number of days to forecast
    """
    return await api_call("POST", "/api/v1/forecast/compare", json_data={
        "sku_id": sku_id,
        "forecast_days": forecast_days
    })


# ==================== ROUTE OPTIMIZATION TOOLS ====================

@mcp.tool()
async def optimize_picking_route(pick_list: list, method: str = "nn+2opt") -> dict:
    """Optimize the picking route for a list of shelf locations.

    Args:
        pick_list: List of shelf locations (e.g., ['A05-3', 'B12-2', 'C03-1'])
        method: Optimization method - 'nn' (nearest neighbor), '2opt', or 'nn+2opt' (combined)
    """
    return await api_call("POST", "/api/v1/routes/optimize", json_data={
        "pick_list": pick_list,
        "method": method
    })


@mcp.tool()
async def batch_optimize_routes(orders_pick_lists: list, picker_capacity: int = 8) -> dict:
    """Optimize routes for multiple orders using batch picking.

    Args:
        orders_pick_lists: List of pick lists, one per order
        picker_capacity: Maximum items a picker can carry (1-20)
    """
    return await api_call("POST", "/api/v1/routes/batch", json_data={
        "orders_pick_lists": orders_pick_lists,
        "picker_capacity": picker_capacity
    })


# ==================== ANOMALY DETECTION TOOLS ====================

@mcp.tool()
async def detect_order_anomalies(contamination: float = 0.05) -> dict:
    """Detect anomalous orders using Isolation Forest.

    Args:
        contamination: Expected proportion of anomalies (0.01-0.20)
    """
    return await api_call("POST", "/api/v1/anomalies/orders", json_data={
        "contamination": contamination
    })


@mcp.tool()
async def detect_inventory_anomalies() -> dict:
    """Detect inventory anomalies using Z-score analysis.

    Returns items with unusual stock levels or expiry issues.
    """
    return await api_call("GET", "/api/v1/anomalies/inventory")


@mcp.tool()
async def detect_staff_anomalies() -> dict:
    """Detect staff performance anomalies.

    Returns staff members with unusual performance metrics.
    """
    return await api_call("GET", "/api/v1/anomalies/staff")


# ==================== AFFINITY ANALYSIS TOOLS ====================

@mcp.tool()
async def get_product_affinities(top_n: int = 20, min_lift: float = 1.0) -> dict:
    """Get frequently co-purchased product pairs.

    Args:
        top_n: Number of top pairs to return (1-100)
        min_lift: Minimum lift threshold (higher = stronger association)
    """
    return await api_call("GET", "/api/v1/affinity/pairs", params={
        "top_n": top_n,
        "min_lift": min_lift
    })


@mcp.tool()
async def get_colocation_recommendations(distance_threshold: int = 50) -> dict:
    """Get recommendations for co-locating frequently purchased items.

    Args:
        distance_threshold: Maximum acceptable distance between items (10-200)
    """
    return await api_call("GET", "/api/v1/affinity/recommendations", params={
        "distance_threshold": distance_threshold
    })


# ==================== SIMULATION TOOLS ====================

@mcp.tool()
async def run_simulation(scenario_type: str, duration_hours: int = 8,
                        orders_per_hour: int = 20, uplift_factor: float = 5.0,
                        delay_days: int = 3) -> dict:
    """Run a simulation scenario.

    Args:
        scenario_type: 'normal', 'flash_sale', or 'supply_delay'
        duration_hours: Duration of simulation (1-24)
        orders_per_hour: Orders per hour (for normal scenario)
        uplift_factor: Demand multiplier (for flash_sale scenario)
        delay_days: Days of supply delay (for supply_delay scenario)
    """
    return await api_call("POST", "/api/v1/simulate/scenario", json_data={
        "scenario_type": scenario_type,
        "duration_hours": duration_hours,
        "orders_per_hour": orders_per_hour,
        "uplift_factor": uplift_factor,
        "delay_days": delay_days
    })


# ==================== DASHBOARD DATA TOOLS ====================

@mcp.tool()
async def get_dashboard_kpis() -> dict:
    """Get summary KPIs for the darkstore dashboard.

    Returns metrics like order counts, on-time rate, revenue, alerts, etc.
    """
    return await api_call("GET", "/api/v1/data/kpis")


@mcp.tool()
async def get_low_stock_items(limit: int = 20) -> dict:
    """Get items with low stock levels and reorder recommendations.

    Args:
        limit: Maximum number of items to return (1-100)
    """
    return await api_call("GET", "/api/v1/data/inventory/low-stock", params={
        "limit": limit
    })


# ==================== RESOURCES ====================

@mcp.resource("schema://orders")
def orders_schema() -> str:
    """Schema for the orders table."""
    return json.dumps({
        "table": "orders",
        "columns": {
            "order_id": "string - Unique order identifier",
            "timestamp": "datetime - Order placement time",
            "num_items": "int - Number of distinct SKUs",
            "total_quantity": "int - Total items in order",
            "total_value": "float - Order value in dollars",
            "status": "string - Pending/Picking/Packing/Delivered",
            "assigned_staff": "string - Staff ID assigned to order",
            "fulfillment_time_minutes": "float - Total fulfillment time",
            "is_delayed": "bool - Whether order missed target",
            "target_time_minutes": "int - Target fulfillment time",
            "items": "json - Array of {sku, qty} objects"
        }
    }, indent=2)


@mcp.resource("schema://inventory")
def inventory_schema() -> str:
    """Schema for the inventory table."""
    return json.dumps({
        "table": "inventory",
        "columns": {
            "sku_id": "string - Unique SKU identifier",
            "product_name": "string - Product description",
            "category": "string - Product category",
            "current_stock": "int - Current stock level",
            "reorder_threshold": "int - Reorder trigger level",
            "shelf_location": "string - Warehouse location (e.g., A05-3)",
            "unit_price": "float - Price per unit",
            "expiry_date": "date - Product expiry date",
            "demand_rate": "string - low/medium/high"
        }
    }, indent=2)


@mcp.resource("config://warehouse")
def warehouse_config() -> str:
    """Warehouse layout configuration."""
    return json.dumps({
        "layout": {
            "aisles": "A-Z (26 aisles)",
            "bays_per_aisle": 20,
            "shelves_per_bay": 5,
            "location_format": "AISLE+BAY-SHELF (e.g., A05-3)",
            "entrance": "Origin (0,0)",
            "packing_station": "Origin (0,0)"
        },
        "dimensions": {
            "aisle_spacing": "10 units",
            "bay_spacing": "5 units",
            "walking_speed": "1.4 m/s",
            "pick_time_per_item": "30 seconds"
        }
    }, indent=2)


if __name__ == "__main__":
    mcp.run(show_banner=False, log_level="ERROR")
