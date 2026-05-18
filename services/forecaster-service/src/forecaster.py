"""Multi-model forecasting engine for forecaster-service."""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
import warnings
import os
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings('ignore')

_default_db_path = Path(__file__).parent.parent.parent.parent / "data" / "dark_store.db"
DB_PATH = Path(os.getenv("DB_PATH", str(_default_db_path)))


class ForecastModel:
    """Base class for forecast models."""

    def __init__(self, name: str):
        self.name = name
        self.model = None
        self.fitted = False

    def fit(self, y: np.array, X: Optional[np.array] = None):
        raise NotImplementedError

    def predict(self, steps: int, X: Optional[np.array] = None) -> Tuple[np.array, np.array, np.array]:
        raise NotImplementedError


class ARIMAModel(ForecastModel):
    def __init__(self, order=(1, 1, 1)):
        super().__init__(f"ARIMA{order}")
        self.order = order

    def fit(self, y: np.array, X: Optional[np.array] = None):
        try:
            self.model = ARIMA(y, order=self.order)
            self.fitted_model = self.model.fit()
            self.fitted = True
        except Exception as e:
            warnings.warn(f"ARIMA fit failed: {e}")
            self.fitted = False

    def predict(self, steps: int, X: Optional[np.array] = None) -> Tuple[np.array, np.array, np.array]:
        if not self.fitted:
            return np.zeros(steps), np.zeros(steps), np.zeros(steps)

        forecast_result = self.fitted_model.forecast(steps=steps)
        forecast = forecast_result if isinstance(forecast_result, np.ndarray) else forecast_result.values

        forecast_obj = self.fitted_model.get_forecast(steps=steps)
        conf_int = forecast_obj.conf_int()

        lower_ci = conf_int.iloc[:, 0].values if hasattr(conf_int, 'iloc') else conf_int[:, 0]
        upper_ci = conf_int.iloc[:, 1].values if hasattr(conf_int, 'iloc') else conf_int[:, 1]

        return np.maximum(forecast, 0), np.maximum(lower_ci, 0), np.maximum(upper_ci, 0)


class SARIMAModel(ForecastModel):
    def __init__(self, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7)):
        super().__init__(f"SARIMA{order}x{seasonal_order}")
        self.order = order
        self.seasonal_order = seasonal_order

    def fit(self, y: np.array, X: Optional[np.array] = None):
        try:
            self.model = SARIMAX(y, order=self.order, seasonal_order=self.seasonal_order)
            self.fitted_model = self.model.fit(disp=False)
            self.fitted = True
        except Exception as e:
            warnings.warn(f"SARIMA fit failed: {e}")
            self.fitted = False

    def predict(self, steps: int, X: Optional[np.array] = None) -> Tuple[np.array, np.array, np.array]:
        if not self.fitted:
            return np.zeros(steps), np.zeros(steps), np.zeros(steps)

        forecast_result = self.fitted_model.forecast(steps=steps)
        forecast = forecast_result if isinstance(forecast_result, np.ndarray) else forecast_result.values

        forecast_obj = self.fitted_model.get_forecast(steps=steps)
        conf_int = forecast_obj.conf_int()

        lower_ci = conf_int.iloc[:, 0].values if hasattr(conf_int, 'iloc') else conf_int[:, 0]
        upper_ci = conf_int.iloc[:, 1].values if hasattr(conf_int, 'iloc') else conf_int[:, 1]

        return np.maximum(forecast, 0), np.maximum(lower_ci, 0), np.maximum(upper_ci, 0)


class HoltWintersModel(ForecastModel):
    def __init__(self, seasonal_periods=7):
        super().__init__("HoltWinters")
        self.seasonal_periods = seasonal_periods

    def fit(self, y: np.array, X: Optional[np.array] = None):
        try:
            if len(y) >= 2 * self.seasonal_periods:
                self.model = ExponentialSmoothing(
                    y,
                    seasonal_periods=self.seasonal_periods,
                    trend='add',
                    seasonal='add'
                )
            else:
                self.model = ExponentialSmoothing(y, trend='add')

            self.fitted_model = self.model.fit()
            self.fitted = True
        except Exception as e:
            warnings.warn(f"Holt-Winters fit failed: {e}")
            self.fitted = False

    def predict(self, steps: int, X: Optional[np.array] = None) -> Tuple[np.array, np.array, np.array]:
        if not self.fitted:
            return np.zeros(steps), np.zeros(steps), np.zeros(steps)

        forecast = self.fitted_model.forecast(steps=steps)

        residuals = self.fitted_model.resid
        std_error = np.std(residuals)
        z_score = 1.96
        margin = z_score * std_error * np.sqrt(1 + np.arange(1, steps + 1) * 0.1)

        lower_ci = forecast - margin
        upper_ci = forecast + margin

        return np.maximum(forecast, 0), np.maximum(lower_ci, 0), np.maximum(upper_ci, 0)


class MLModel(ForecastModel):
    def __init__(self, model_type='gbm'):
        super().__init__(f"ML_{model_type}")
        self.model_type = model_type

        if model_type == 'rf':
            self.model = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
        else:
            self.model = GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)

        self.y_train = None

    def create_features(self, y: np.array, start_idx: int = 0) -> np.array:
        n = len(y)
        features = []

        for i in range(n):
            abs_idx = start_idx + i
            feat = [
                abs_idx,
                abs_idx % 7,
                y[i-1] if i > 0 else y[0],
                y[i-7] if i >= 7 else y[0],
                np.mean(y[max(0, i-7):i+1]),
                np.std(y[max(0, i-7):i+1]) if i > 0 else 0,
            ]
            features.append(feat)

        return np.array(features)

    def fit(self, y: np.array, X: Optional[np.array] = None):
        try:
            if len(y) < 10:
                self.fitted = False
                return

            self.y_train = y
            X_train = self.create_features(y)

            self.model.fit(X_train, y)
            self.fitted = True
        except Exception as e:
            warnings.warn(f"ML model fit failed: {e}")
            self.fitted = False

    def predict(self, steps: int, X: Optional[np.array] = None) -> Tuple[np.array, np.array, np.array]:
        if not self.fitted:
            return np.zeros(steps), np.zeros(steps), np.zeros(steps)

        forecast = []
        y_extended = list(self.y_train)
        start_idx = len(self.y_train)

        for step in range(steps):
            X_pred = self.create_features(np.array(y_extended), start_idx=0)[-1:]
            pred = self.model.predict(X_pred)[0]
            pred = max(pred, 0)
            forecast.append(pred)
            y_extended.append(pred)

        forecast = np.array(forecast)

        X_train = self.create_features(self.y_train)
        train_pred = self.model.predict(X_train)
        residuals = self.y_train - train_pred
        std_error = np.std(residuals)

        margin = 1.96 * std_error * np.sqrt(1 + np.arange(1, steps + 1) * 0.15)
        lower_ci = forecast - margin
        upper_ci = forecast + margin

        return forecast, np.maximum(lower_ci, 0), np.maximum(upper_ci, 0)


class MultiModelForecaster:
    def __init__(self, orders_df: pd.DataFrame, inventory_df: pd.DataFrame):
        self.orders_df = orders_df.copy()
        self.inventory_df = inventory_df.copy()

        if 'timestamp' in self.orders_df.columns:
            self.orders_df['timestamp'] = pd.to_datetime(self.orders_df['timestamp'])

        self._prepare_demand_data()

        self.models = {
            'arima': ARIMAModel(order=(1, 1, 1)),
            'sarima': SARIMAModel(order=(1, 1, 1), seasonal_order=(1, 1, 1, 7)),
            'holt_winters': HoltWintersModel(seasonal_periods=7),
            'rf': MLModel('rf'),
            'gbm': MLModel('gbm'),
        }

        self.model_performance = {}

    def _prepare_demand_data(self):
        items_list = []
        for _, order in self.orders_df.iterrows():
            items = json.loads(order['items']) if isinstance(order['items'], str) else order['items']
            for item in items:
                items_list.append({
                    'date': order['timestamp'].date(),
                    'sku_id': item['sku'],
                    'quantity': item['qty']
                })

        self.items_df = pd.DataFrame(items_list)
        self.items_df['date'] = pd.to_datetime(self.items_df['date'])

    def get_sku_series(self, sku_id: str) -> Tuple[Optional[np.array], Optional[pd.DatetimeIndex]]:
        sku_data = self.items_df[self.items_df['sku_id'] == sku_id].copy()

        if len(sku_data) == 0:
            return None, None

        daily_demand = sku_data.groupby('date')['quantity'].sum().reset_index()
        daily_demand = daily_demand.sort_values('date')

        date_range = pd.date_range(
            start=daily_demand['date'].min(),
            end=daily_demand['date'].max(),
            freq='D'
        )
        full_range = pd.DataFrame({'date': date_range})
        daily_demand = full_range.merge(daily_demand, on='date', how='left')
        daily_demand['quantity'] = daily_demand['quantity'].fillna(0)

        return daily_demand['quantity'].values, daily_demand['date']

    def rolling_origin_cv(self, y: np.array, model: ForecastModel,
                          horizon: int = 7, n_splits: int = 3) -> Optional[Dict]:
        min_required = max(10, horizon * 2)
        if len(y) < min_required:
            return None

        if len(y) < 20:
            n_splits = min(2, n_splits)

        errors = {'mae': [], 'rmse': [], 'mape': []}

        min_train_size = max(14, len(y) // 2)
        test_points = np.linspace(min_train_size, len(y) - horizon, n_splits, dtype=int)

        for split_point in test_points:
            train = y[:split_point]
            test = y[split_point:split_point + horizon]

            if len(test) < horizon:
                continue

            try:
                model.fit(train)
                forecast, _, _ = model.predict(len(test))

                errors['mae'].append(mean_absolute_error(test, forecast))
                errors['rmse'].append(np.sqrt(mean_squared_error(test, forecast)))

                test_nonzero = test[test > 0]
                forecast_nonzero = forecast[test > 0]
                if len(test_nonzero) > 0:
                    mape = np.mean(np.abs((test_nonzero - forecast_nonzero) / test_nonzero)) * 100
                    errors['mape'].append(mape)

            except Exception as e:
                warnings.warn(f"CV fold failed for {model.name}: {e}")
                continue

        if len(errors['mae']) == 0:
            return None

        return {
            'mean_mae': np.mean(errors['mae']),
            'mean_rmse': np.mean(errors['rmse']),
            'mean_mape': np.mean(errors['mape']) if len(errors['mape']) > 0 else np.inf,
            'std_mape': np.std(errors['mape']) if len(errors['mape']) > 0 else np.inf,
            'n_folds': len(errors['mae'])
        }

    def select_best_model(self, sku_id: str, y: np.array) -> str:
        if len(y) < 7:
            return 'holt_winters'

        results = {}

        for model_name, model in self.models.items():
            cv_results = self.rolling_origin_cv(y, model, horizon=7, n_splits=3)
            if cv_results is not None:
                results[model_name] = cv_results

        if len(results) == 0:
            return 'holt_winters'

        valid_models = {
            name: metrics for name, metrics in results.items()
            if metrics['std_mape'] < 50
        }

        if len(valid_models) == 0:
            valid_models = results

        best_model = min(valid_models.items(), key=lambda x: x[1]['mean_mape'])

        self.model_performance[sku_id] = {
            'selected_model': best_model[0],
            'all_results': results,
            'selection_time': datetime.now().isoformat()
        }

        return best_model[0]

    def create_ensemble(self, forecasts: Dict[str, np.array],
                       weights: Optional[Dict[str, float]] = None) -> np.array:
        if weights is None:
            weights = {name: 1.0 / len(forecasts) for name in forecasts.keys()}

        ensemble = np.zeros(len(list(forecasts.values())[0]))

        for model_name, forecast in forecasts.items():
            ensemble += weights.get(model_name, 0) * forecast

        return ensemble

    def forecast_sku(self, sku_id: str, forecast_days: int = 14, mode: str = 'auto') -> Dict:
        y, dates = self.get_sku_series(sku_id)

        if y is None or len(y) < 5:
            return {
                'sku_id': sku_id,
                'has_data': False,
                'message': 'Insufficient historical data'
            }

        if mode == 'auto':
            selected_model_name = self.select_best_model(sku_id, y)
        elif mode == 'ensemble':
            selected_model_name = None
        else:
            selected_model_name = mode if mode in self.models else 'holt_winters'

        all_forecasts = {}

        if selected_model_name:
            model = self.models[selected_model_name]
            model.fit(y)
            forecast, lower_ci, upper_ci = model.predict(forecast_days)
            all_forecasts[selected_model_name] = forecast
        else:
            for model_name, model in self.models.items():
                try:
                    model.fit(y)
                    forecast, _, _ = model.predict(forecast_days)
                    all_forecasts[model_name] = forecast
                except Exception as e:
                    warnings.warn(f"Model {model_name} failed: {e}")

            if len(all_forecasts) > 0:
                forecast = self.create_ensemble(all_forecasts)
                forecast_array = np.array(list(all_forecasts.values()))
                lower_ci = np.percentile(forecast_array, 5, axis=0)
                upper_ci = np.percentile(forecast_array, 95, axis=0)
                selected_model_name = 'ensemble'
            else:
                return {
                    'sku_id': sku_id,
                    'has_data': False,
                    'message': 'All models failed'
                }

        last_date = dates.max()
        future_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]

        avg_historical = np.mean(y)
        avg_forecast = np.mean(forecast)
        trend = 'Increasing' if avg_forecast > avg_historical * 1.1 else \
                'Decreasing' if avg_forecast < avg_historical * 0.9 else 'Stable'

        result = {
            'sku_id': sku_id,
            'has_data': True,
            'model_used': selected_model_name,
            'historical_days': len(y),
            'historical_demand': y.tolist(),
            'historical_dates': dates.dt.strftime('%Y-%m-%d').tolist(),
            'forecast_days': forecast_days,
            'forecast': forecast.tolist(),
            'lower_ci': lower_ci.tolist(),
            'upper_ci': upper_ci.tolist(),
            'forecast_dates': [d.strftime('%Y-%m-%d') for d in future_dates],
            'avg_historical_daily': float(round(avg_historical, 2)),
            'avg_forecast_daily': float(round(avg_forecast, 2)),
            'trend': trend,
            'total_forecast_demand': float(round(np.sum(forecast), 1)),
            'all_models': list(all_forecasts.keys()) if mode == 'ensemble' else None
        }

        product_info = self.inventory_df[self.inventory_df['sku_id'] == sku_id]
        if len(product_info) > 0:
            result['product_name'] = product_info.iloc[0]['product_name']
            result['category'] = product_info.iloc[0]['category']
            result['current_stock'] = int(product_info.iloc[0]['current_stock'])
            result['reorder_threshold'] = int(product_info.iloc[0]['reorder_threshold'])
            result['needs_reorder'] = bool(result['current_stock'] < result['total_forecast_demand'])

        return result

    def compare_models(self, sku_id: str, forecast_days: int = 14) -> Dict:
        y, dates = self.get_sku_series(sku_id)

        if y is None:
            return {'error': 'No historical data available for this SKU'}

        if len(y) < 3:
            return {'error': f'Insufficient data: only {len(y)} days available (minimum 3 days required)'}

        comparison = {
            'sku_id': sku_id,
            'models': {},
            'data_length': len(y),
            'data_warning': 'Limited historical data - CV metrics may be unavailable' if len(y) < 20 else None
        }

        for model_name, model in self.models.items():
            try:
                cv_results = None
                if len(y) >= max(10, forecast_days * 2):
                    try:
                        cv_results = self.rolling_origin_cv(y, model, horizon=min(7, forecast_days), n_splits=2)
                    except Exception:
                        pass

                model.fit(y)
                forecast, lower_ci, upper_ci = model.predict(forecast_days)

                comparison['models'][model_name] = {
                    'forecast': forecast.tolist(),
                    'lower_ci': lower_ci.tolist(),
                    'upper_ci': upper_ci.tolist(),
                    'cv_results': cv_results,
                    'avg_forecast': float(np.mean(forecast)),
                    'status': 'success'
                }
            except Exception as e:
                comparison['models'][model_name] = {
                    'error': str(e),
                    'status': 'failed'
                }

        successful_models = [m for m in comparison['models'].values() if m.get('status') == 'success']

        if len(successful_models) == 0:
            return {'error': 'All models failed to generate forecasts'}

        return comparison


_forecaster = None

def get_forecaster() -> MultiModelForecaster:
    global _forecaster
    if _forecaster is None:
        conn = sqlite3.connect(str(DB_PATH))
        orders_df = pd.read_sql_query("SELECT * FROM orders", conn)
        inventory_df = pd.read_sql_query("SELECT * FROM inventory", conn)
        conn.close()
        _forecaster = MultiModelForecaster(orders_df, inventory_df)
    return _forecaster
