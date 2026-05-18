"""Event simulation engine for event-simulator-service."""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import random
import os
from enum import Enum
from dataclasses import dataclass, asdict
import sqlite3
from pathlib import Path

_default_db_path = Path(__file__).parent.parent.parent.parent / "data" / "dark_store.db"
DB_PATH = Path(os.getenv("DB_PATH", str(_default_db_path)))


class EventType(Enum):
    ORDER_PLACED = "order_placed"
    ORDER_CANCELLED = "order_cancelled"
    PICK_STARTED = "pick_started"
    PICK_COMPLETED = "pick_completed"
    PACK_STARTED = "pack_started"
    PACK_COMPLETED = "pack_completed"
    DELIVERY_DISPATCHED = "delivery_dispatched"
    DELIVERY_COMPLETED = "delivery_completed"
    INVENTORY_ADJUSTMENT = "inventory_adjustment"
    RESTOCK_RECEIVED = "restock_received"
    LOW_STOCK_ALERT = "low_stock_alert"
    STOCKOUT = "stockout"


@dataclass
class Event:
    event_id: str
    event_type: EventType
    timestamp: datetime
    payload: Dict
    metadata: Dict = None

    def to_dict(self):
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'payload': self.payload,
            'metadata': self.metadata or {}
        }


class EventGenerator:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        self.random = random.Random(seed)
        self.event_counter = 0

    def generate_event_id(self) -> str:
        self.event_counter += 1
        return f"EVT_{self.seed}_{self.event_counter:06d}"

    def reset(self):
        self.rng = np.random.RandomState(self.seed)
        self.random = random.Random(self.seed)
        self.event_counter = 0


class OrderEventGenerator(EventGenerator):
    def __init__(self, skus: List[str], seed: int = 42):
        super().__init__(seed)
        self.skus = skus

    def generate_order_placed(self, timestamp: datetime, avg_items: int = 8) -> Event:
        n_items = max(1, int(self.rng.poisson(avg_items)))
        selected_skus = self.random.choices(self.skus, k=min(n_items, len(self.skus)))

        items = []
        for sku in selected_skus:
            items.append({
                'sku': sku,
                'qty': int(self.rng.poisson(2)) + 1
            })

        order_id = f"ORD_{timestamp.strftime('%Y%m%d')}_{self.event_counter:04d}"

        return Event(
            event_id=self.generate_event_id(),
            event_type=EventType.ORDER_PLACED,
            timestamp=timestamp,
            payload={
                'order_id': order_id,
                'items': items,
                'customer_id': f"CUST_{self.rng.randint(1000, 9999)}",
                'priority': self.random.choice(['normal', 'normal', 'normal', 'express'])
            },
            metadata={'generator': 'OrderEventGenerator'}
        )

    def generate_pick_started(self, order_event: Event, delay_minutes: float = 2) -> Event:
        timestamp = order_event.timestamp + timedelta(minutes=delay_minutes)

        return Event(
            event_id=self.generate_event_id(),
            event_type=EventType.PICK_STARTED,
            timestamp=timestamp,
            payload={
                'order_id': order_event.payload['order_id'],
                'picker_id': f"PICK_{self.rng.randint(1, 10):02d}",
                'items': order_event.payload['items']
            },
            metadata={'order_event_id': order_event.event_id}
        )

    def generate_pick_completed(self, pick_event: Event, duration_minutes: float = 8) -> Event:
        timestamp = pick_event.timestamp + timedelta(minutes=duration_minutes)

        return Event(
            event_id=self.generate_event_id(),
            event_type=EventType.PICK_COMPLETED,
            timestamp=timestamp,
            payload={
                'order_id': pick_event.payload['order_id'],
                'picker_id': pick_event.payload['picker_id'],
                'items_picked': len(pick_event.payload['items']),
                'duration_minutes': duration_minutes
            },
            metadata={'pick_event_id': pick_event.event_id}
        )


class InventoryEventGenerator(EventGenerator):
    def __init__(self, inventory_df: pd.DataFrame, seed: int = 42):
        super().__init__(seed)
        self.inventory_df = inventory_df.copy()
        self.current_stock = dict(zip(
            inventory_df['sku_id'],
            inventory_df['current_stock']
        ))

    def update_stock(self, sku_id: str, delta: int):
        if sku_id in self.current_stock:
            self.current_stock[sku_id] = max(0, self.current_stock[sku_id] + delta)

    def check_and_generate_alerts(self, timestamp: datetime) -> List[Event]:
        alerts = []

        for _, row in self.inventory_df.iterrows():
            sku_id = row['sku_id']
            threshold = row['reorder_threshold']
            current = self.current_stock.get(sku_id, 0)

            if current == 0:
                alerts.append(Event(
                    event_id=self.generate_event_id(),
                    event_type=EventType.STOCKOUT,
                    timestamp=timestamp,
                    payload={
                        'sku_id': sku_id,
                        'product_name': row['product_name'],
                        'category': row['category']
                    }
                ))
            elif current < threshold:
                alerts.append(Event(
                    event_id=self.generate_event_id(),
                    event_type=EventType.LOW_STOCK_ALERT,
                    timestamp=timestamp,
                    payload={
                        'sku_id': sku_id,
                        'product_name': row['product_name'],
                        'current_stock': current,
                        'reorder_threshold': threshold,
                        'deficit': threshold - current
                    }
                ))

        return alerts


class ScenarioGenerator:
    def __init__(self, orders_df: pd.DataFrame, inventory_df: pd.DataFrame, seed: int = 42):
        self.orders_df = orders_df
        self.inventory_df = inventory_df
        self.seed = seed
        self.skus = inventory_df['sku_id'].tolist()
        self.order_gen = OrderEventGenerator(self.skus, seed)
        self.inventory_gen = InventoryEventGenerator(inventory_df, seed)

    def reset(self):
        self.order_gen.reset()
        self.inventory_gen.reset()

    def generate_normal_day(self, start_time: datetime, duration_hours: int = 12,
                           orders_per_hour: int = 20) -> List[Event]:
        events = []
        current_time = start_time

        for hour in range(duration_hours):
            n_orders = int(self.order_gen.rng.poisson(orders_per_hour))

            arrival_times = sorted([
                current_time + timedelta(minutes=self.order_gen.rng.uniform(0, 60))
                for _ in range(n_orders)
            ])

            for arrival_time in arrival_times:
                order_event = self.order_gen.generate_order_placed(arrival_time)
                events.append(order_event)

                pick_delay = self.order_gen.rng.uniform(1, 5)
                pick_event = self.order_gen.generate_pick_started(order_event, pick_delay)
                events.append(pick_event)

                pick_duration = self.order_gen.rng.uniform(5, 15)
                pick_complete = self.order_gen.generate_pick_completed(pick_event, pick_duration)
                events.append(pick_complete)

                for item in order_event.payload['items']:
                    self.inventory_gen.update_stock(item['sku'], -item['qty'])

            current_time += timedelta(hours=1)
            alerts = self.inventory_gen.check_and_generate_alerts(current_time)
            events.extend(alerts)

        return sorted(events, key=lambda e: e.timestamp)

    def generate_flash_sale(self, start_time: datetime, duration_hours: int = 3,
                           sale_skus: Optional[List[str]] = None,
                           uplift_factor: float = 5.0) -> List[Event]:
        if sale_skus is None:
            sale_skus = self.skus[:10]

        events = []
        current_time = start_time
        orders_per_hour = int(50 * uplift_factor)

        for hour in range(duration_hours):
            n_orders = int(self.order_gen.rng.poisson(orders_per_hour))

            arrival_times = sorted([
                current_time + timedelta(minutes=self.order_gen.rng.uniform(0, 60))
                for _ in range(n_orders)
            ])

            for arrival_time in arrival_times:
                n_items = max(1, int(self.order_gen.rng.poisson(4)))
                items = []
                for _ in range(n_items):
                    if self.order_gen.random.random() < 0.7:
                        sku = self.order_gen.random.choice(sale_skus)
                    else:
                        sku = self.order_gen.random.choice(self.skus)
                    items.append({
                        'sku': sku,
                        'qty': int(self.order_gen.rng.poisson(2)) + 1
                    })

                order_id = f"ORD_FLASH_{arrival_time.strftime('%Y%m%d_%H%M')}_{len(events):04d}"

                order_event = Event(
                    event_id=self.order_gen.generate_event_id(),
                    event_type=EventType.ORDER_PLACED,
                    timestamp=arrival_time,
                    payload={
                        'order_id': order_id,
                        'items': items,
                        'customer_id': f"CUST_{self.order_gen.rng.randint(1000, 9999)}",
                        'priority': 'express',
                        'flash_sale': True
                    },
                    metadata={'scenario': 'flash_sale'}
                )
                events.append(order_event)

                pick_delay = self.order_gen.rng.uniform(3, 10)
                pick_event = self.order_gen.generate_pick_started(order_event, pick_delay)
                events.append(pick_event)

                pick_duration = self.order_gen.rng.uniform(10, 20)
                pick_complete = self.order_gen.generate_pick_completed(pick_event, pick_duration)
                events.append(pick_complete)

                for item in items:
                    self.inventory_gen.update_stock(item['sku'], -item['qty'])

            current_time += timedelta(hours=1)
            alerts = self.inventory_gen.check_and_generate_alerts(current_time)
            events.extend(alerts)

        return sorted(events, key=lambda e: e.timestamp)

    def generate_supply_delay(self, start_time: datetime,
                             affected_skus: Optional[List[str]] = None,
                             delay_days: int = 3) -> List[Event]:
        if affected_skus is None:
            n_affected = int(len(self.skus) * 0.2)
            affected_skus = self.order_gen.random.sample(self.skus, n_affected)

        events = []

        for sku in affected_skus:
            current_stock = self.inventory_gen.current_stock.get(sku, 0)

            if current_stock > 0:
                daily_depletion = max(1, int(current_stock / delay_days))

                for day in range(delay_days):
                    event_time = start_time + timedelta(days=day)

                    self.inventory_gen.update_stock(sku, -daily_depletion)

                    events.append(Event(
                        event_id=self.inventory_gen.generate_event_id(),
                        event_type=EventType.INVENTORY_ADJUSTMENT,
                        timestamp=event_time,
                        payload={
                            'sku_id': sku,
                            'delta': -daily_depletion,
                            'new_stock': self.inventory_gen.current_stock[sku],
                            'reason': 'demand_with_supply_delay'
                        }
                    ))

                    alerts = self.inventory_gen.check_and_generate_alerts(event_time)
                    events.extend(alerts)

        restock_time = start_time + timedelta(days=delay_days)
        for sku in affected_skus:
            sku_info = self.inventory_df[self.inventory_df['sku_id'] == sku]
            if len(sku_info) > 0:
                reorder_qty = int(sku_info.iloc[0]['reorder_threshold'] * 2)
                self.inventory_gen.update_stock(sku, reorder_qty)

                events.append(Event(
                    event_id=self.inventory_gen.generate_event_id(),
                    event_type=EventType.RESTOCK_RECEIVED,
                    timestamp=restock_time,
                    payload={
                        'sku_id': sku,
                        'quantity': reorder_qty,
                        'new_stock': self.inventory_gen.current_stock[sku],
                        'supplier_id': f"SUP_{self.inventory_gen.rng.randint(1, 5):02d}"
                    }
                ))

        return sorted(events, key=lambda e: e.timestamp)


class EventSimulator:
    def __init__(self, orders_df: pd.DataFrame, inventory_df: pd.DataFrame, seed: int = 42):
        self.orders_df = orders_df
        self.inventory_df = inventory_df
        self.seed = seed
        self.scenario_gen = ScenarioGenerator(orders_df, inventory_df, seed)
        self.events: List[Event] = []

    def generate_scenario(self, scenario_type: str, start_time: Optional[datetime] = None,
                         **kwargs) -> List[Event]:
        if start_time is None:
            start_time = datetime.now()

        self.scenario_gen.reset()

        if scenario_type == 'normal':
            events = self.scenario_gen.generate_normal_day(start_time, **kwargs)
        elif scenario_type == 'flash_sale':
            events = self.scenario_gen.generate_flash_sale(start_time, **kwargs)
        elif scenario_type == 'supply_delay':
            events = self.scenario_gen.generate_supply_delay(start_time, **kwargs)
        else:
            raise ValueError(f"Unknown scenario type: {scenario_type}")

        self.events = events
        return events

    def get_metrics(self) -> Dict:
        if not self.events:
            return {}

        event_counts = {}
        for event in self.events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        order_events = [e for e in self.events if e.event_type == EventType.ORDER_PLACED]
        pick_complete_events = [e for e in self.events if e.event_type == EventType.PICK_COMPLETED]

        if pick_complete_events:
            avg_pick_time = np.mean([
                e.payload.get('duration_minutes', 0)
                for e in pick_complete_events
            ])
        else:
            avg_pick_time = 0

        alert_events = [e for e in self.events if e.event_type in [EventType.LOW_STOCK_ALERT, EventType.STOCKOUT]]

        return {
            'total_events': len(self.events),
            'event_counts': event_counts,
            'total_orders': len(order_events),
            'avg_pick_time_minutes': round(avg_pick_time, 2),
            'total_alerts': len(alert_events),
            'start_time': self.events[0].timestamp.isoformat() if self.events else None,
            'end_time': self.events[-1].timestamp.isoformat() if self.events else None,
        }


_simulator = None

def get_simulator() -> EventSimulator:
    global _simulator
    if _simulator is None:
        conn = sqlite3.connect(str(DB_PATH))
        orders_df = pd.read_sql_query("SELECT * FROM orders LIMIT 100", conn)
        inventory_df = pd.read_sql_query("SELECT * FROM inventory", conn)
        conn.close()
        _simulator = EventSimulator(orders_df, inventory_df)
    return _simulator
