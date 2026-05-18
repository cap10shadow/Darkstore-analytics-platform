"""Anomaly detection engine for anomaly-detector-service."""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from scipy import stats
from typing import List, Dict
import sqlite3
import os
from pathlib import Path
from datetime import datetime

_default_db_path = Path(__file__).parent.parent.parent.parent / "data" / "dark_store.db"
DB_PATH = Path(os.getenv("DB_PATH", str(_default_db_path)))


class AnomalyDetector:
    def __init__(self, orders_df: pd.DataFrame, inventory_df: pd.DataFrame):
        self.orders_df = orders_df.copy()
        self.inventory_df = inventory_df.copy()

        if 'timestamp' in self.orders_df.columns:
            self.orders_df['timestamp'] = pd.to_datetime(self.orders_df['timestamp'])

    def detect_order_fulfillment_anomalies(self, contamination: float = 0.05) -> List[Dict]:
        features = self.orders_df[[
            'num_items',
            'total_quantity',
            'fulfillment_time_minutes'
        ]].copy()

        features['hour'] = self.orders_df['timestamp'].dt.hour
        features['day_of_week'] = self.orders_df['timestamp'].dt.dayofweek
        features['is_weekend'] = (features['day_of_week'] >= 5).astype(int)

        features = features.fillna(features.mean())

        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)

        iso_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )

        predictions = iso_forest.fit_predict(features_scaled)
        anomaly_scores = iso_forest.score_samples(features_scaled)

        results = self.orders_df[[
            'order_id', 'timestamp', 'num_items', 'total_quantity',
            'fulfillment_time_minutes', 'target_time_minutes', 'assigned_staff', 'status'
        ]].copy()

        results['is_anomaly'] = (predictions == -1)
        results['anomaly_score'] = anomaly_scores

        anomalies = results[results['is_anomaly']].copy()

        anomaly_list = []
        for _, order in anomalies.iterrows():
            types = []
            reason_parts = []

            if order['fulfillment_time_minutes'] > order['target_time_minutes'] * 2:
                types.append('Severe Delay')
                reason_parts.append(f"Took {order['fulfillment_time_minutes']:.1f} min (target: {order['target_time_minutes']} min)")
            elif order['fulfillment_time_minutes'] < 5 and order['num_items'] > 3:
                types.append('Suspiciously Fast')
                reason_parts.append(f"Only {order['fulfillment_time_minutes']:.1f} min for {order['num_items']} items")
            elif order['num_items'] > 6 and order['fulfillment_time_minutes'] > 40:
                types.append('Large Order Delay')
                reason_parts.append(f"{order['num_items']} items took {order['fulfillment_time_minutes']:.1f} min")

            if not types:
                types.append('Statistical Outlier')
                reason_parts.append(f"Anomaly score: {order['anomaly_score']:.3f}")

            anomaly_list.append({
                'order_id': order['order_id'],
                'timestamp': order['timestamp'].isoformat(),
                'num_items': int(order['num_items']),
                'total_quantity': int(order['total_quantity']),
                'fulfillment_time_minutes': float(order['fulfillment_time_minutes']),
                'target_time_minutes': int(order['target_time_minutes']),
                'assigned_staff': order['assigned_staff'],
                'status': order['status'],
                'is_anomaly': True,
                'anomaly_score': float(order['anomaly_score']),
                'anomaly_type': ', '.join(types),
                'reason': '; '.join(reason_parts)
            })

        return sorted(anomaly_list, key=lambda x: x['anomaly_score'])

    def detect_inventory_anomalies(self) -> List[Dict]:
        inventory = self.inventory_df.copy()

        inventory['stock_zscore'] = stats.zscore(inventory['current_stock'])
        inventory['is_stock_anomaly'] = np.abs(inventory['stock_zscore']) > 3

        inventory['days_until_expiry'] = (
            pd.to_datetime(inventory['expiry_date']) - datetime.now()
        ).dt.days

        inventory['is_expiry_anomaly'] = (
            (inventory['days_until_expiry'] < 0) |
            ((inventory['days_until_expiry'] < 3) & (inventory['current_stock'] > inventory['reorder_threshold']))
        )

        anomalies = inventory[
            inventory['is_stock_anomaly'] | inventory['is_expiry_anomaly']
        ].copy()

        anomaly_list = []
        for _, item in anomalies.iterrows():
            types = []
            reason_parts = []

            if item['is_stock_anomaly']:
                if item['stock_zscore'] > 3:
                    types.append('Excessive Stock')
                    reason_parts.append(f"Stock ({item['current_stock']}) is unusually high (z={item['stock_zscore']:.1f})")
                else:
                    types.append('Abnormally Low Stock')
                    reason_parts.append(f"Stock ({item['current_stock']}) is unusually low (z={item['stock_zscore']:.1f})")

            if item['is_expiry_anomaly']:
                if item['days_until_expiry'] < 0:
                    types.append('Expired Product')
                    reason_parts.append(f"Expired {abs(item['days_until_expiry'])} days ago")
                else:
                    types.append('High Stock Near Expiry')
                    reason_parts.append(f"Expires in {item['days_until_expiry']} days with {item['current_stock']} units")

            anomaly_list.append({
                'sku_id': item['sku_id'],
                'product_name': item['product_name'],
                'category': item['category'],
                'current_stock': int(item['current_stock']),
                'reorder_threshold': int(item['reorder_threshold']),
                'expiry_date': str(item['expiry_date']) if pd.notna(item['expiry_date']) else None,
                'anomaly_type': ', '.join(types),
                'reason': '; '.join(reason_parts),
                'stock_zscore': float(item['stock_zscore'])
            })

        return anomaly_list

    def detect_staff_performance_anomalies(self) -> List[Dict]:
        staff_metrics = self.orders_df.groupby('assigned_staff').agg({
            'order_id': 'count',
            'fulfillment_time_minutes': ['mean', 'std'],
            'is_delayed': 'sum'
        }).reset_index()

        staff_metrics.columns = ['staff_id', 'total_orders', 'avg_time', 'std_time', 'delays']

        if len(staff_metrics) > 2:
            staff_metrics['time_zscore'] = stats.zscore(staff_metrics['avg_time'])
            staff_metrics['delay_rate'] = staff_metrics['delays'] / staff_metrics['total_orders']
            staff_metrics['delay_zscore'] = stats.zscore(staff_metrics['delay_rate'])

            anomalies = []

            for _, staff in staff_metrics.iterrows():
                if staff['staff_id'] == 'UNASSIGNED':
                    continue

                types = []
                reasons = []

                if staff['time_zscore'] > 2:
                    types.append('Slow Performance')
                    reasons.append(f"Avg time {staff['avg_time']:.1f} min (z={staff['time_zscore']:.1f})")

                if staff['delay_zscore'] > 2:
                    types.append('High Delay Rate')
                    reasons.append(f"{staff['delay_rate']*100:.1f}% delays (z={staff['delay_zscore']:.1f})")

                if staff['total_orders'] < staff_metrics['total_orders'].mean() * 0.5:
                    types.append('Low Productivity')
                    reasons.append(f"Only {staff['total_orders']} orders (avg: {staff_metrics['total_orders'].mean():.0f})")

                if types:
                    anomalies.append({
                        'staff_id': staff['staff_id'],
                        'anomaly_type': ', '.join(types),
                        'reason': '; '.join(reasons),
                        'total_orders': int(staff['total_orders']),
                        'avg_fulfillment_time': round(staff['avg_time'], 1),
                        'delay_rate': round(staff['delay_rate'] * 100, 1)
                    })

            return anomalies

        return []


_detector = None

def get_detector() -> AnomalyDetector:
    global _detector
    if _detector is None:
        conn = sqlite3.connect(str(DB_PATH))
        orders_df = pd.read_sql_query("SELECT * FROM orders", conn)
        inventory_df = pd.read_sql_query("SELECT * FROM inventory", conn)
        conn.close()
        _detector = AnomalyDetector(orders_df, inventory_df)
    return _detector
