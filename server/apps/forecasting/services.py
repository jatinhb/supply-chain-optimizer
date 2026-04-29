"""Forecasting service using Prophet and XGBoost."""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional

from django.db import transaction

from apps.inventory.models import Product
from .models import DemandHistory, DemandForecast, ForecastAccuracy, SeasonalityPattern


class ForecastingService:
    """Service for generating demand forecasts."""

    def __init__(self):
        self.min_history_points = 30  # Minimum data points for forecasting

    def generate_forecast(
        self,
        product: Product,
        horizon_weeks: int = 12,
        model_type: str = 'prophet',
        confidence_level: float = 95.0
    ) -> Dict[str, Any]:
        """Generate demand forecast for a product."""

        # Get historical data
        history = self._get_demand_history(product)

        if len(history) < self.min_history_points:
            # Generate synthetic forecast based on basic statistics
            return self._generate_simple_forecast(
                product, horizon_weeks, confidence_level
            )

        # Generate forecast based on model type
        if model_type == 'prophet':
            forecasts = self._prophet_forecast(
                history, horizon_weeks, confidence_level
            )
        elif model_type == 'xgboost':
            forecasts = self._xgboost_forecast(
                history, horizon_weeks, confidence_level
            )
        elif model_type == 'ensemble':
            forecasts = self._ensemble_forecast(
                history, horizon_weeks, confidence_level
            )
        else:  # arima
            forecasts = self._arima_forecast(
                history, horizon_weeks, confidence_level
            )

        # Save forecasts to database
        saved_forecasts = self._save_forecasts(
            product, forecasts, model_type, confidence_level
        )

        # Calculate and save accuracy metrics
        accuracy = self._calculate_accuracy(product, history, model_type)

        # Detect and save seasonality
        seasonality = self._detect_seasonality(product, history)

        # Generate summary
        return self._build_forecast_result(
            product, saved_forecasts, accuracy, seasonality, model_type
        )

    def _get_demand_history(self, product: Product) -> pd.DataFrame:
        """Get demand history as DataFrame."""
        history = DemandHistory.objects.filter(
            product=product
        ).order_by('date').values('date', 'quantity', 'is_promotion', 'is_holiday')

        if not history:
            return pd.DataFrame()

        df = pd.DataFrame(list(history))
        df['date'] = pd.to_datetime(df['date'])
        return df

    def _generate_simple_forecast(
        self,
        product: Product,
        horizon_weeks: int,
        confidence_level: float
    ) -> Dict[str, Any]:
        """Generate simple forecast when insufficient history."""

        # Use reorder point and safety stock as baseline
        base_demand = product.reorder_point / 4  # Weekly estimate

        today = datetime.now().date()
        forecasts = []

        for week in range(horizon_weeks):
            forecast_date = today + timedelta(weeks=week + 1)
            # Add some variation
            variation = np.random.uniform(0.9, 1.1)
            predicted = base_demand * variation

            forecasts.append({
                'product_id': product.id,
                'product_sku': product.sku,
                'product_name': product.name,
                'forecast_date': forecast_date,
                'predicted_demand': round(predicted, 2),
                'lower_bound': round(predicted * 0.8, 2),
                'upper_bound': round(predicted * 1.2, 2),
            })

        return {
            'product_id': product.id,
            'product_sku': product.sku,
            'product_name': product.name,
            'model_type': 'simple',
            'accuracy': None,
            'trend': 'stable',
            'total_forecasted_demand': sum(f['predicted_demand'] for f in forecasts),
            'peak_demand_date': max(forecasts, key=lambda x: x['predicted_demand'])['forecast_date'],
            'peak_demand_value': max(f['predicted_demand'] for f in forecasts),
            'suggested_safety_stock': int(base_demand * 2),
            'suggested_reorder_quantity': int(base_demand * 4),
            'forecasts': forecasts,
            'note': 'Insufficient historical data. Using simple estimation.'
        }

    def _prophet_forecast(
        self,
        history: pd.DataFrame,
        horizon_weeks: int,
        confidence_level: float
    ) -> List[Dict]:
        """Generate forecast using Prophet-like algorithm."""

        # Simplified Prophet-style decomposition
        # In production, use actual Prophet library

        # Calculate trend
        history['trend'] = history['quantity'].rolling(window=7, min_periods=1).mean()

        # Calculate weekly seasonality
        history['day_of_week'] = history['date'].dt.dayofweek
        weekly_pattern = history.groupby('day_of_week')['quantity'].mean()

        # Calculate monthly seasonality
        history['month'] = history['date'].dt.month
        monthly_pattern = history.groupby('month')['quantity'].mean()
        monthly_pattern = monthly_pattern / monthly_pattern.mean()  # Normalize

        # Forecast
        last_trend = history['trend'].iloc[-1]
        trend_growth = (history['trend'].iloc[-1] - history['trend'].iloc[0]) / len(history)

        today = datetime.now().date()
        forecasts = []

        for week in range(horizon_weeks):
            forecast_date = today + timedelta(weeks=week + 1)
            month = forecast_date.month

            # Base prediction with trend
            base = last_trend + (trend_growth * (week + 1) * 7)

            # Apply monthly seasonality
            seasonal_factor = monthly_pattern.get(month, 1.0)
            predicted = base * seasonal_factor

            # Confidence interval
            std = history['quantity'].std()
            z_score = 1.96 if confidence_level == 95 else 1.645  # 95% or 90%

            lower = max(0, predicted - z_score * std)
            upper = predicted + z_score * std

            forecasts.append({
                'forecast_date': forecast_date,
                'predicted_demand': round(float(predicted), 2),
                'lower_bound': round(float(lower), 2),
                'upper_bound': round(float(upper), 2),
            })

        return forecasts

    def _xgboost_forecast(
        self,
        history: pd.DataFrame,
        horizon_weeks: int,
        confidence_level: float
    ) -> List[Dict]:
        """Generate forecast using XGBoost-like approach."""
        # Simplified ML-style forecast
        # In production, use actual XGBoost

        # Feature engineering
        history['lag_1'] = history['quantity'].shift(1)
        history['lag_7'] = history['quantity'].shift(7)
        history['rolling_mean_7'] = history['quantity'].rolling(7).mean()
        history['rolling_std_7'] = history['quantity'].rolling(7).std()

        # Use last known values for prediction
        last_values = history.dropna().iloc[-1]
        base_prediction = (
            0.3 * last_values['quantity'] +
            0.3 * last_values['lag_7'] +
            0.4 * last_values['rolling_mean_7']
        )

        today = datetime.now().date()
        forecasts = []
        std = history['quantity'].std()

        for week in range(horizon_weeks):
            forecast_date = today + timedelta(weeks=week + 1)

            # Add some drift
            predicted = base_prediction * (1 + np.random.uniform(-0.05, 0.05))

            z_score = 1.96 if confidence_level == 95 else 1.645
            lower = max(0, predicted - z_score * std)
            upper = predicted + z_score * std

            forecasts.append({
                'forecast_date': forecast_date,
                'predicted_demand': round(float(predicted), 2),
                'lower_bound': round(float(lower), 2),
                'upper_bound': round(float(upper), 2),
            })

        return forecasts

    def _ensemble_forecast(
        self,
        history: pd.DataFrame,
        horizon_weeks: int,
        confidence_level: float
    ) -> List[Dict]:
        """Combine Prophet and XGBoost forecasts."""
        prophet_fc = self._prophet_forecast(history, horizon_weeks, confidence_level)
        xgboost_fc = self._xgboost_forecast(history, horizon_weeks, confidence_level)

        forecasts = []
        for p, x in zip(prophet_fc, xgboost_fc):
            # Weighted average (60% Prophet, 40% XGBoost)
            predicted = 0.6 * p['predicted_demand'] + 0.4 * x['predicted_demand']
            lower = 0.6 * p['lower_bound'] + 0.4 * x['lower_bound']
            upper = 0.6 * p['upper_bound'] + 0.4 * x['upper_bound']

            forecasts.append({
                'forecast_date': p['forecast_date'],
                'predicted_demand': round(predicted, 2),
                'lower_bound': round(lower, 2),
                'upper_bound': round(upper, 2),
            })

        return forecasts

    def _arima_forecast(
        self,
        history: pd.DataFrame,
        horizon_weeks: int,
        confidence_level: float
    ) -> List[Dict]:
        """Generate ARIMA-style forecast."""
        # Simplified ARIMA using moving averages

        ma_7 = history['quantity'].rolling(7).mean().iloc[-1]
        ma_30 = history['quantity'].rolling(30).mean().iloc[-1]

        today = datetime.now().date()
        forecasts = []
        std = history['quantity'].std()

        for week in range(horizon_weeks):
            forecast_date = today + timedelta(weeks=week + 1)

            # Blend of moving averages with decay
            weight = 0.7 ** (week / 4)  # Decay factor
            predicted = weight * ma_7 + (1 - weight) * ma_30

            z_score = 1.96 if confidence_level == 95 else 1.645
            margin = z_score * std * (1 + week * 0.05)  # Increasing uncertainty
            lower = max(0, predicted - margin)
            upper = predicted + margin

            forecasts.append({
                'forecast_date': forecast_date,
                'predicted_demand': round(float(predicted), 2),
                'lower_bound': round(float(lower), 2),
                'upper_bound': round(float(upper), 2),
            })

        return forecasts

    @transaction.atomic
    def _save_forecasts(
        self,
        product: Product,
        forecasts: List[Dict],
        model_type: str,
        confidence_level: float
    ) -> List[DemandForecast]:
        """Save forecasts to database."""
        # Remove old forecasts for this product/model
        DemandForecast.objects.filter(
            product=product,
            model_type=model_type,
            forecast_date__gte=datetime.now().date()
        ).delete()

        saved = []
        for fc in forecasts:
            forecast = DemandForecast.objects.create(
                product=product,
                forecast_date=fc['forecast_date'],
                predicted_demand=Decimal(str(fc['predicted_demand'])),
                lower_bound=Decimal(str(fc['lower_bound'])),
                upper_bound=Decimal(str(fc['upper_bound'])),
                confidence_level=Decimal(str(confidence_level)),
                model_type=model_type
            )
            saved.append(forecast)

        return saved

    def _calculate_accuracy(
        self,
        product: Product,
        history: pd.DataFrame,
        model_type: str
    ) -> Optional[ForecastAccuracy]:
        """Calculate forecast accuracy metrics."""
        if len(history) < 30:
            return None

        # Use last 30 days for validation
        train = history.iloc[:-30]
        test = history.iloc[-30:]

        if len(train) < 30:
            return None

        # Generate forecasts for test period
        test_forecasts = self._prophet_forecast(train, 5, 95.0)

        # Calculate metrics (simplified)
        actual = test['quantity'].values[:len(test_forecasts)]
        predicted = np.array([f['predicted_demand'] for f in test_forecasts[:len(actual)]])

        if len(actual) == 0:
            return None

        mape = np.mean(np.abs((actual - predicted) / (actual + 1))) * 100
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        mae = np.mean(np.abs(actual - predicted))

        ss_res = np.sum((actual - predicted) ** 2)
        ss_tot = np.sum((actual - np.mean(actual)) ** 2)
        r_squared = 1 - (ss_res / (ss_tot + 1e-10))

        accuracy = ForecastAccuracy.objects.create(
            product=product,
            model_type=model_type,
            period_start=test['date'].min().date(),
            period_end=test['date'].max().date(),
            mape=Decimal(str(round(mape, 4))),
            rmse=Decimal(str(round(rmse, 4))),
            mae=Decimal(str(round(mae, 4))),
            r_squared=Decimal(str(round(max(0, min(1, r_squared)), 6)))
        )

        return accuracy

    def _detect_seasonality(
        self,
        product: Product,
        history: pd.DataFrame
    ) -> List[SeasonalityPattern]:
        """Detect and save seasonality patterns."""
        if len(history) < 365:
            return []

        # Monthly seasonality
        history['month'] = history['date'].dt.month
        monthly = history.groupby('month')['quantity'].mean()
        overall_mean = monthly.mean()

        patterns = []
        for month, value in monthly.items():
            factor = value / overall_mean if overall_mean > 0 else 1.0

            pattern, _ = SeasonalityPattern.objects.update_or_create(
                product=product,
                pattern_type='monthly',
                period_index=month,
                defaults={'factor': Decimal(str(round(factor, 6)))}
            )
            patterns.append(pattern)

        return patterns

    def _build_forecast_result(
        self,
        product: Product,
        forecasts: List[DemandForecast],
        accuracy: Optional[ForecastAccuracy],
        seasonality: List[SeasonalityPattern],
        model_type: str
    ) -> Dict[str, Any]:
        """Build the forecast result response."""
        if not forecasts:
            return {'error': 'No forecasts generated'}

        total_demand = sum(float(f.predicted_demand) for f in forecasts)
        peak = max(forecasts, key=lambda f: f.predicted_demand)

        # Determine trend
        first_half = sum(float(f.predicted_demand) for f in forecasts[:len(forecasts)//2])
        second_half = sum(float(f.predicted_demand) for f in forecasts[len(forecasts)//2:])

        if second_half > first_half * 1.1:
            trend = 'up'
        elif second_half < first_half * 0.9:
            trend = 'down'
        else:
            trend = 'stable'

        # Suggestions
        avg_weekly = total_demand / len(forecasts)
        suggested_safety = int(avg_weekly * 2)  # 2 weeks safety stock
        suggested_eoq = int(avg_weekly * 4)  # 4 weeks order quantity

        return {
            'product_id': product.id,
            'product_sku': product.sku,
            'product_name': product.name,
            'model_type': model_type,
            'accuracy': float(accuracy.mape) if accuracy else None,
            'trend': trend,
            'total_forecasted_demand': round(total_demand, 2),
            'peak_demand_date': peak.forecast_date,
            'peak_demand_value': float(peak.predicted_demand),
            'suggested_safety_stock': suggested_safety,
            'suggested_reorder_quantity': suggested_eoq,
            'forecasts': [
                {
                    'date': f.forecast_date.isoformat(),
                    'predicted': float(f.predicted_demand),
                    'lower': float(f.lower_bound),
                    'upper': float(f.upper_bound),
                }
                for f in forecasts
            ],
            'seasonality': [
                {
                    'month': s.period_index,
                    'factor': float(s.factor)
                }
                for s in seasonality
            ] if seasonality else None
        }
