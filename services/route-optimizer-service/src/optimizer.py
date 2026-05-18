"""Route optimization engine for route-optimizer-service."""
from typing import List, Tuple, Dict


class WarehouseLayout:
    def __init__(self):
        self.locations = {}
        self._generate_layout()

    def _generate_layout(self):
        for aisle_idx in range(26):
            aisle = chr(65 + aisle_idx)
            x_base = aisle_idx * 10

            for bay in range(1, 21):
                y = bay * 5

                for shelf in range(1, 6):
                    location_code = f"{aisle}{bay:02d}-{shelf}"
                    self.locations[location_code] = (x_base, y)

        self.locations['ENTRANCE'] = (0, 0)
        self.locations['PACKING'] = (0, 0)

    def get_coordinates(self, location_code: str) -> Tuple[float, float]:
        return self.locations.get(location_code, (0, 0))

    def distance(self, loc1: str, loc2: str) -> float:
        x1, y1 = self.get_coordinates(loc1)
        x2, y2 = self.get_coordinates(loc2)
        return abs(x2 - x1) + abs(y2 - y1)


class RouteOptimizer:
    def __init__(self, warehouse: WarehouseLayout = None):
        self.warehouse = warehouse or WarehouseLayout()

    def nearest_neighbor(self, start: str, locations: List[str]) -> List[str]:
        if not locations:
            return []

        route = []
        current = start
        remaining = locations.copy()

        while remaining:
            nearest = min(remaining, key=lambda loc: self.warehouse.distance(current, loc))
            route.append(nearest)
            current = nearest
            remaining.remove(nearest)

        return route

    def two_opt(self, route: List[str], start: str = 'ENTRANCE', end: str = 'PACKING') -> List[str]:
        if len(route) < 2:
            return route

        improved = True
        best_route = route.copy()

        while improved:
            improved = False
            best_distance = self._route_distance([start] + best_route + [end])

            for i in range(len(best_route) - 1):
                for j in range(i + 2, len(best_route)):
                    new_route = best_route[:i] + best_route[i:j][::-1] + best_route[j:]
                    new_distance = self._route_distance([start] + new_route + [end])

                    if new_distance < best_distance:
                        best_route = new_route
                        best_distance = new_distance
                        improved = True
                        break

                if improved:
                    break

        return best_route

    def _route_distance(self, route: List[str]) -> float:
        if len(route) < 2:
            return 0

        total = 0
        for i in range(len(route) - 1):
            total += self.warehouse.distance(route[i], route[i + 1])
        return total

    def optimize_route(self, pick_list: List[str], method: str = 'nn+2opt') -> Dict:
        if not pick_list:
            return {
                'route': [],
                'coordinates': [],
                'distance': 0,
                'naive_distance': 0,
                'estimated_time_minutes': 0,
                'improvement_percent': 0,
                'num_stops': 0
            }

        naive_route = pick_list.copy()
        naive_distance = self._route_distance(['ENTRANCE'] + naive_route + ['PACKING'])

        if method == 'nn':
            optimized_route = self.nearest_neighbor('ENTRANCE', pick_list)
        elif method == '2opt':
            optimized_route = self.two_opt(pick_list, 'ENTRANCE', 'PACKING')
        else:  # nn+2opt
            nn_route = self.nearest_neighbor('ENTRANCE', pick_list)
            optimized_route = self.two_opt(nn_route, 'ENTRANCE', 'PACKING')

        optimized_distance = self._route_distance(['ENTRANCE'] + optimized_route + ['PACKING'])

        improvement = ((naive_distance - optimized_distance) / naive_distance * 100) if naive_distance > 0 else 0

        # If optimization made it worse, use the naive route instead
        if improvement < 0:
            optimized_route = naive_route
            optimized_distance = naive_distance
            improvement = 0

        picking_time = len(pick_list) * 0.5
        walking_time = optimized_distance / 1.4 / 60
        total_time = picking_time + walking_time

        full_route = ['ENTRANCE'] + optimized_route + ['PACKING']

        return {
            'route': full_route,
            'coordinates': [self.warehouse.get_coordinates(loc) for loc in full_route],
            'distance': round(optimized_distance, 2),
            'naive_distance': round(naive_distance, 2),
            'estimated_time_minutes': round(total_time, 2),
            'improvement_percent': round(improvement, 1),
            'num_stops': len(pick_list)
        }

    def batch_route(self, orders_pick_lists: List[List[str]], picker_capacity: int = 8) -> List[Dict]:
        batches = []
        current_batch = []

        for pick_list in orders_pick_lists:
            if len(current_batch) + len(pick_list) <= picker_capacity:
                current_batch.extend(pick_list)
            else:
                if current_batch:
                    batches.append(self.optimize_route(current_batch))
                current_batch = pick_list.copy()

        if current_batch:
            batches.append(self.optimize_route(current_batch))

        return batches


_optimizer = None

def get_optimizer() -> RouteOptimizer:
    global _optimizer
    if _optimizer is None:
        _optimizer = RouteOptimizer()
    return _optimizer
