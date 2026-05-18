"""Affinity analysis engine for affinity-analyzer-service."""
import pandas as pd
import numpy as np
from collections import Counter
from itertools import combinations
from typing import List, Dict
import json
import sqlite3
import os
from pathlib import Path

_default_db_path = Path(__file__).parent.parent.parent.parent / "data" / "dark_store.db"
DB_PATH = Path(os.getenv("DB_PATH", str(_default_db_path)))


class AffinityAnalyzer:
    def __init__(self, orders_df: pd.DataFrame, inventory_df: pd.DataFrame):
        self.orders_df = orders_df
        self.inventory_df = inventory_df
        self.transactions = self._extract_transactions()

    def _extract_transactions(self) -> List[List[str]]:
        transactions = []
        for _, order in self.orders_df.iterrows():
            items = json.loads(order['items']) if isinstance(order['items'], str) else order['items']
            skus = [item['sku'] for item in items]
            if len(skus) > 1:
                transactions.append(skus)
        return transactions

    def compute_co_occurrence(self, min_support: int = 5) -> pd.DataFrame:
        item_counts = Counter()
        for transaction in self.transactions:
            item_counts.update(transaction)

        pair_counts = Counter()
        for transaction in self.transactions:
            for pair in combinations(sorted(transaction), 2):
                pair_counts[pair] += 1

        results = []
        total_transactions = len(self.transactions)

        for (sku_a, sku_b), count in pair_counts.items():
            if count >= min_support:
                support = count / total_transactions

                confidence_a_to_b = count / item_counts[sku_a]
                confidence_b_to_a = count / item_counts[sku_b]

                expected = (item_counts[sku_a] / total_transactions) * (item_counts[sku_b] / total_transactions)
                lift = support / expected if expected > 0 else 0

                affinity = (confidence_a_to_b + confidence_b_to_a) / 2 * lift

                results.append({
                    'sku_a': sku_a,
                    'sku_b': sku_b,
                    'co_occurrences': count,
                    'support': round(support, 4),
                    'confidence_a_to_b': round(confidence_a_to_b, 4),
                    'confidence_b_to_a': round(confidence_b_to_a, 4),
                    'lift': round(lift, 2),
                    'affinity_score': round(affinity, 4)
                })

        df = pd.DataFrame(results)
        if len(df) > 0:
            df = df.sort_values('affinity_score', ascending=False)

        return df

    def get_top_pairs(self, top_n: int = 20, min_lift: float = 1.0) -> List[Dict]:
        affinity_df = self.compute_co_occurrence()

        if len(affinity_df) == 0:
            return []

        affinity_df = affinity_df[affinity_df['lift'] >= min_lift]

        affinity_df = affinity_df.merge(
            self.inventory_df[['sku_id', 'product_name', 'category', 'shelf_location']],
            left_on='sku_a',
            right_on='sku_id',
            how='left'
        ).rename(columns={'product_name': 'product_a', 'category': 'category_a', 'shelf_location': 'location_a'})

        affinity_df = affinity_df.merge(
            self.inventory_df[['sku_id', 'product_name', 'category', 'shelf_location']],
            left_on='sku_b',
            right_on='sku_id',
            how='left'
        ).rename(columns={'product_name': 'product_b', 'category': 'category_b', 'shelf_location': 'location_b'})

        result = []
        for _, row in affinity_df.head(top_n).iterrows():
            result.append({
                'sku_a': row['sku_a'],
                'product_a': row['product_a'],
                'category_a': row['category_a'],
                'location_a': row['location_a'],
                'sku_b': row['sku_b'],
                'product_b': row['product_b'],
                'category_b': row['category_b'],
                'location_b': row['location_b'],
                'co_occurrences': int(row['co_occurrences']),
                'confidence_a_to_b': float(row['confidence_a_to_b']),
                'lift': float(row['lift']),
                'affinity_score': float(row['affinity_score'])
            })

        return result

    def get_colocation_recommendations(self, distance_threshold: int = 50) -> List[Dict]:
        top_pairs = self.get_top_pairs(top_n=20, min_lift=1.5)

        if len(top_pairs) == 0:
            return []

        recommendations = []

        for pair in top_pairs:
            loc_a = pair['location_a']
            loc_b = pair['location_b']

            try:
                aisle_a = ord(loc_a[0]) - 65
                bay_a = int(loc_a[1:3])
                aisle_b = ord(loc_b[0]) - 65
                bay_b = int(loc_b[1:3])

                current_distance = abs(aisle_a - aisle_b) * 10 + abs(bay_a - bay_b) * 5

                if current_distance > distance_threshold:
                    time_saved_per_pick = (current_distance - distance_threshold) / 1.4 / 60
                    annual_picks = pair['co_occurrences'] * 52
                    annual_time_saved = time_saved_per_pick * annual_picks

                    recommendations.append({
                        'sku_a': pair['sku_a'],
                        'sku_b': pair['sku_b'],
                        'product_a': pair['product_a'],
                        'product_b': pair['product_b'],
                        'current_distance': round(current_distance, 1),
                        'co_occurrences_weekly': pair['co_occurrences'],
                        'affinity_score': pair['affinity_score'],
                        'lift': pair['lift'],
                        'estimated_annual_time_saved_hours': round(annual_time_saved / 60, 1),
                        'recommendation': f"Move {pair['sku_a']} closer to {pair['sku_b']} (currently {current_distance:.0f} units apart)",
                        'priority': 'High' if pair['lift'] > 2.0 else 'Medium'
                    })
            except (ValueError, IndexError, TypeError):
                continue

        recommendations.sort(key=lambda x: x['estimated_annual_time_saved_hours'], reverse=True)

        return recommendations[:10]


_analyzer = None

def get_analyzer() -> AffinityAnalyzer:
    global _analyzer
    if _analyzer is None:
        conn = sqlite3.connect(str(DB_PATH))
        orders_df = pd.read_sql_query("SELECT order_id, items FROM orders", conn)
        inventory_df = pd.read_sql_query("SELECT * FROM inventory", conn)
        conn.close()
        _analyzer = AffinityAnalyzer(orders_df, inventory_df)
    return _analyzer
