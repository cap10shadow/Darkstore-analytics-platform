"""Database connection and data loading for data-service."""
import pandas as pd
import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

_default_db_path = Path(__file__).parent.parent.parent.parent / "data" / "dark_store.db"
DB_PATH = Path(os.getenv("DB_PATH", str(_default_db_path)))


class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(DB_PATH)
        self._conn = None

    def get_connection(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None


class DataProcessor:
    def __init__(self, db: Database):
        self.db = db
        self.inventory_df = None
        self.orders_df = None
        self.staff_df = None
        self.alerts_df = None

    def load_data(self):
        conn = self.db.get_connection()

        self.inventory_df = pd.read_sql_query("SELECT * FROM inventory", conn)
        self.orders_df = pd.read_sql_query("SELECT * FROM orders", conn)
        self.staff_df = pd.read_sql_query("SELECT * FROM staff", conn)
        self.alerts_df = pd.read_sql_query("SELECT * FROM alerts", conn)

        # Convert timestamps
        self.orders_df['timestamp'] = pd.to_datetime(self.orders_df['timestamp'])

        for col in ['pick_start_time', 'pick_end_time', 'pack_end_time', 'estimated_delivery', 'delivery_time']:
            if col in self.orders_df.columns:
                self.orders_df[col] = pd.to_datetime(self.orders_df[col])

        if 'timestamp' in self.alerts_df.columns:
            self.alerts_df['timestamp'] = pd.to_datetime(self.alerts_df['timestamp'])
        if 'expiry_date' in self.inventory_df.columns:
            self.inventory_df['expiry_date'] = pd.to_datetime(self.inventory_df['expiry_date'])

        return self

    def get_summary_kpis(self) -> dict:
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        today_orders = self.orders_df[self.orders_df['timestamp'] >= yesterday]

        total_orders_today = len(today_orders)
        total_orders_all = len(self.orders_df)

        on_time_orders = len(self.orders_df[
            self.orders_df['fulfillment_time_minutes'] <= self.orders_df['target_time_minutes']
        ])
        on_time_rate = (on_time_orders / total_orders_all * 100) if total_orders_all > 0 else 0

        backlog = len(self.orders_df[self.orders_df['status'].isin(['Pending', 'Picking', 'Packing'])])
        avg_fulfillment = self.orders_df['fulfillment_time_minutes'].mean()

        total_revenue = self.orders_df['total_value'].sum()
        revenue_today = today_orders['total_value'].sum()

        low_stock_count = len(self.inventory_df[
            self.inventory_df['current_stock'] < self.inventory_df['reorder_threshold']
        ])
        total_skus = len(self.inventory_df)
        stock_health_rate = ((total_skus - low_stock_count) / total_skus * 100) if total_skus > 0 else 0

        active_alerts = len(self.alerts_df[self.alerts_df['status'] == 'Open'])
        critical_alerts = len(self.alerts_df[
            (self.alerts_df['status'] == 'Open') & (self.alerts_df['severity'] == 'Critical')
        ])

        return {
            'total_orders_today': total_orders_today,
            'total_orders_all': total_orders_all,
            'on_time_rate': round(on_time_rate, 1),
            'backlog': backlog,
            'avg_fulfillment_minutes': round(avg_fulfillment, 1),
            'total_revenue': round(total_revenue, 2),
            'revenue_today': round(revenue_today, 2),
            'low_stock_count': low_stock_count,
            'total_skus': total_skus,
            'stock_health_rate': round(stock_health_rate, 1),
            'active_alerts': active_alerts,
            'critical_alerts': critical_alerts
        }

    def get_orders(self, limit: int = 100, offset: int = 0) -> list:
        orders = self.orders_df.iloc[offset:offset + limit].copy()
        result = []

        for _, row in orders.iterrows():
            items = json.loads(row['items']) if isinstance(row['items'], str) else row['items']
            result.append({
                'order_id': row['order_id'],
                'timestamp': row['timestamp'].isoformat(),
                'num_items': row['num_items'],
                'total_quantity': row['total_quantity'],
                'total_value': row['total_value'],
                'status': row['status'],
                'assigned_staff': row['assigned_staff'],
                'fulfillment_time_minutes': row['fulfillment_time_minutes'],
                'is_delayed': bool(row['is_delayed']),
                'target_time_minutes': row['target_time_minutes'],
                'items': items
            })

        return result

    def get_inventory(self, limit: int = 100, offset: int = 0) -> list:
        inventory = self.inventory_df.iloc[offset:offset + limit].copy()

        inventory['health_status'] = inventory.apply(
            lambda row: 'Critical' if row['current_stock'] < row['reorder_threshold'] * 0.5
            else 'Low' if row['current_stock'] < row['reorder_threshold']
            else 'Healthy',
            axis=1
        )

        inventory['days_until_expiry'] = (
            inventory['expiry_date'] - datetime.now()
        ).dt.days

        result = []
        for _, row in inventory.iterrows():
            result.append({
                'sku_id': row['sku_id'],
                'product_name': row['product_name'],
                'category': row['category'],
                'current_stock': int(row['current_stock']),
                'reorder_threshold': int(row['reorder_threshold']),
                'shelf_location': row['shelf_location'],
                'unit_price': float(row['unit_price']),
                'expiry_date': row['expiry_date'].isoformat() if pd.notna(row['expiry_date']) else None,
                'demand_rate': row['demand_rate'],
                'health_status': row['health_status'],
                'days_until_expiry': float(row['days_until_expiry']) if pd.notna(row['days_until_expiry']) else None
            })

        return result

    def calculate_daily_demand(self) -> pd.DataFrame:
        items_list = []
        for _, order in self.orders_df.iterrows():
            items = json.loads(order['items']) if isinstance(order['items'], str) else order['items']
            for item in items:
                items_list.append({
                    'sku_id': item['sku'],
                    'quantity': item['qty'],
                    'timestamp': order['timestamp']
                })

        if not items_list:
            return pd.DataFrame(columns=['sku_id', 'daily_demand'])

        items_df = pd.DataFrame(items_list)
        days_in_data = (self.orders_df['timestamp'].max() - self.orders_df['timestamp'].min()).days
        days_in_data = max(days_in_data, 1)

        sku_demand = items_df.groupby('sku_id')['quantity'].sum().reset_index()
        sku_demand['daily_demand'] = (sku_demand['quantity'] / days_in_data).round(2)

        return sku_demand[['sku_id', 'daily_demand']]

    def get_low_stock_items(self, limit: int = 20) -> list:
        daily_demand = self.calculate_daily_demand()

        low_stock = self.inventory_df[
            self.inventory_df['current_stock'] < self.inventory_df['reorder_threshold']
        ].copy()

        if len(low_stock) == 0:
            return []

        low_stock = low_stock.merge(daily_demand, on='sku_id', how='left')
        low_stock['daily_demand'] = low_stock['daily_demand'].fillna(0)

        low_stock['stock_percentage'] = (
            low_stock['current_stock'] / low_stock['reorder_threshold'] * 100
        ).round(1)

        low_stock['days_until_stockout'] = low_stock.apply(
            lambda row: (row['current_stock'] / row['daily_demand']) if row['daily_demand'] > 0 else 999,
            axis=1
        ).round(1)

        SAFETY_STOCK_DAYS = 2
        COVERAGE_DAYS = 7

        low_stock['recommended_order_qty'] = low_stock.apply(
            lambda row: max(
                int((row['daily_demand'] * (COVERAGE_DAYS + SAFETY_STOCK_DAYS)) - row['current_stock']),
                int(row['reorder_threshold'] * 1.5)
            ),
            axis=1
        )

        low_stock['estimated_cost'] = (
            low_stock['recommended_order_qty'] * low_stock['unit_price']
        ).round(2)

        low_stock = low_stock.sort_values('stock_percentage')

        result = []
        for _, row in low_stock.head(limit).iterrows():
            result.append({
                'sku_id': row['sku_id'],
                'product_name': row['product_name'],
                'category': row['category'],
                'current_stock': int(row['current_stock']),
                'reorder_threshold': int(row['reorder_threshold']),
                'stock_percentage': float(row['stock_percentage']),
                'daily_demand': float(row['daily_demand']),
                'days_until_stockout': float(row['days_until_stockout']),
                'recommended_order_qty': int(row['recommended_order_qty']),
                'estimated_cost': float(row['estimated_cost'])
            })

        return result

    def get_active_alerts(self, limit: int = 50) -> list:
        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}

        active = self.alerts_df[self.alerts_df['status'] == 'Open'].copy()
        active['severity_rank'] = active['severity'].map(severity_order)
        active = active.sort_values(['severity_rank', 'timestamp'], ascending=[True, False])

        result = []
        for _, row in active.head(limit).iterrows():
            result.append({
                'alert_id': row['alert_id'],
                'alert_type': row['alert_type'],
                'severity': row['severity'],
                'status': row['status'],
                'timestamp': row['timestamp'].isoformat() if pd.notna(row['timestamp']) else None,
                'related_sku': row.get('related_sku') if pd.notna(row.get('related_sku')) else None,
                'related_order': row.get('related_order') if pd.notna(row.get('related_order')) else None,
                'message': row['message']
            })

        return result

    def get_staff_performance(self) -> list:
        staff_orders = self.orders_df.groupby('assigned_staff').agg({
            'order_id': 'count',
            'fulfillment_time_minutes': 'mean',
            'is_delayed': 'sum'
        }).reset_index()

        staff_orders.columns = ['staff_id', 'orders_completed', 'avg_fulfillment_time', 'delays_caused']

        performance = staff_orders.merge(self.staff_df, on='staff_id', how='left')

        performance['orders_per_hour'] = (
            performance['orders_completed'] / (7 * 8)
        ).round(1)

        performance['delay_rate'] = (
            performance['delays_caused'] / performance['orders_completed'] * 100
        ).round(1)

        performance = performance.sort_values('orders_completed', ascending=False)

        result = []
        for _, row in performance.iterrows():
            result.append({
                'staff_id': row['staff_id'],
                'name': row.get('name', 'Unknown'),
                'role': row.get('role', 'Picker'),
                'orders_completed': int(row['orders_completed']),
                'avg_fulfillment_time': round(float(row['avg_fulfillment_time']), 1),
                'delays_caused': int(row['delays_caused']),
                'orders_per_hour': float(row['orders_per_hour']),
                'delay_rate': float(row['delay_rate'])
            })

        return result


# Singleton instance
_db = Database()
_processor = None

def get_processor() -> DataProcessor:
    global _processor
    if _processor is None:
        _processor = DataProcessor(_db)
        _processor.load_data()
    return _processor
