"""Market synthesis and forecasting agent for the StrategyDECK system."""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import statistics
from collections import defaultdict
import math
from ..core.base_agent import BaseAgent


class SynthAgent(BaseAgent):
    """Synth Agent for market synthesis and forecasting."""

    def __init__(self, name: str = "synth", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.market_metrics = defaultdict(list)
        self.forecasting_models = {
            'pricing': self._forecast_pricing,
            'demand': self._forecast_demand,
            'conversion': self._forecast_conversion
        }
        self.synthesis_results = {
            'last_update': None,
            'forecasts': {},
            'correlations': {},
            'anomalies': []
        }
        
        # Subscribe to market-related topics
        self.subscribe_to_topic('market.metrics')
        self.subscribe_to_topic('pricing.data')
        self.subscribe_to_topic('demand.signals')
        self.subscribe_to_topic('market.synthesis')

    def validate_config(self) -> bool:
        """Validate agent configuration."""
        required = ['forecast_horizon', 'confidence_threshold', 'update_interval']
        return all(key in self.config for key in required)

    def run(self) -> Dict[str, Any]:
        """Execute market synthesis and forecasting."""
        results = {
            'synthesis_status': 'nominal',
            'market_insights': {},
            'forecasts': {},
            'recommendations': []
        }

        try:
            # Collect market metrics
            self._collect_market_metrics()

            # Generate market insights
            insights = self._generate_market_insights()
            results['market_insights'] = insights

            # Update forecasts
            forecasts = self._update_forecasts()
            results['forecasts'] = forecasts

            # Process synthesis requests
            synth_requests = self.get_messages('market.synthesis')
            if synth_requests:
                for request in synth_requests:
                    recommendation = self._handle_synthesis_request(request)
                    results['recommendations'].append(recommendation)

            # Check for significant market changes
            if self._detect_significant_changes(insights):
                self._broadcast_market_alert(insights)

            return results

        except Exception as e:
            self.logger.error(f"Market synthesis failed: {str(e)}")
            results['synthesis_status'] = 'error'
            results['error'] = str(e)
            return results

    def _collect_market_metrics(self) -> None:
        """Collect and process market metrics from various sources."""
        metric_messages = self.get_messages('market.metrics')
        for msg in metric_messages:
            metrics = msg.get('data', {})
            for metric_name, value in metrics.items():
                self.market_metrics[metric_name].append({
                    'value': value,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                
                # Trim old metrics
                max_history = self.config.get('metrics_history', 1000)
                if len(self.market_metrics[metric_name]) > max_history:
                    self.market_metrics[metric_name] = \
                        self.market_metrics[metric_name][-max_history:]

    def _generate_market_insights(self) -> Dict[str, Any]:
        """Generate market insights from collected metrics."""
        insights = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics': {},
            'trends': {},
            'correlations': {},
            'anomalies': []
        }

        # Calculate metrics summary
        for metric, values in self.market_metrics.items():
            if not values:
                continue
                
            recent_values = [v['value'] for v in values[-30:]]  # Last 30 data points
            insights['metrics'][metric] = {
                'current': recent_values[-1],
                'mean': statistics.mean(recent_values),
                'median': statistics.median(recent_values),
                'std_dev': statistics.stdev(recent_values) if len(recent_values) > 1 else 0,
                'trend': self._calculate_trend(recent_values)
            }

        # Calculate correlations
        insights['correlations'] = self._calculate_correlations()

        # Detect anomalies
        insights['anomalies'] = self._detect_anomalies()

        return insights

    def _update_forecasts(self) -> Dict[str, Any]:
        """Update market forecasts using different models."""
        forecasts = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'horizon': self.config.get('forecast_horizon', 30),
            'models': {}
        }

        for model_name, forecast_func in self.forecasting_models.items():
            try:
                forecast = forecast_func()
                forecasts['models'][model_name] = {
                    'forecast': forecast,
                    'confidence': self._calculate_forecast_confidence(forecast),
                    'validation': self._validate_forecast(forecast)
                }
            except Exception as e:
                self.logger.error(f"Forecast failed for {model_name}: {str(e)}")
                forecasts['models'][model_name] = {'error': str(e)}

        self.synthesis_results['last_update'] = datetime.now(timezone.utc)
        self.synthesis_results['forecasts'] = forecasts
        return forecasts

    def _handle_synthesis_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a market synthesis request."""
        request_data = request.get('data', {})
        synthesis_type = request_data.get('type')
        parameters = request_data.get('parameters', {})
        
        response = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'type': synthesis_type,
            'status': 'processed'
        }

        try:
            if synthesis_type == 'market_analysis':
                response['analysis'] = self._analyze_market(parameters)
            elif synthesis_type == 'optimization':
                response['optimization'] = self._optimize_strategy(parameters)
            elif synthesis_type == 'forecast':
                response['forecast'] = self._generate_forecast(parameters)
            else:
                response['status'] = 'invalid_request'
                
        except Exception as e:
            response['status'] = 'error'
            response['error'] = str(e)
            
        return response

    def _analyze_market(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform detailed market analysis."""
        analysis = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics': {},
            'segments': [],
            'opportunities': []
        }

        # Analyze key metrics
        for metric, values in self.market_metrics.items():
            if not values:
                continue
                
            recent_values = [v['value'] for v in values[-30:]]
            analysis['metrics'][metric] = {
                'current': recent_values[-1],
                'trend': self._calculate_trend(recent_values),
                'volatility': self._calculate_volatility(recent_values)
            }

        # Identify market segments
        if 'segment_threshold' in parameters:
            analysis['segments'] = self._identify_segments(
                parameters['segment_threshold']
            )

        # Find opportunities
        if analysis['metrics']:
            analysis['opportunities'] = self._identify_opportunities(
                analysis['metrics']
            )

        return analysis

    def _optimize_strategy(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize market strategy based on parameters."""
        optimization = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'recommendations': [],
            'adjustments': {}
        }

        target_metric = parameters.get('target_metric')
        if target_metric in self.market_metrics:
            current_value = self.market_metrics[target_metric][-1]['value']
            target_value = parameters.get('target_value')
            
            if target_value:
                optimization['adjustments'][target_metric] = {
                    'current': current_value,
                    'target': target_value,
                    'suggested_changes': self._calculate_adjustments(
                        current_value, target_value
                    )
                }

        # Generate strategic recommendations
        optimization['recommendations'] = self._generate_recommendations(
            optimization['adjustments']
        )

        return optimization

    def _generate_forecast(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific forecast based on parameters."""
        forecast = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'horizon': parameters.get('horizon', 30),
            'predictions': {},
            'confidence_intervals': {}
        }

        metrics = parameters.get('metrics', list(self.market_metrics.keys()))
        for metric in metrics:
            if metric not in self.market_metrics:
                continue
                
            values = [v['value'] for v in self.market_metrics[metric]]
            predictions = self._forecast_values(values, forecast['horizon'])
            confidence = self._calculate_confidence_intervals(predictions)
            
            forecast['predictions'][metric] = predictions
            forecast['confidence_intervals'][metric] = confidence

        return forecast

    def _forecast_pricing(self) -> Dict[str, Any]:
        """Generate pricing forecasts."""
        pricing_metrics = ['price_elasticity', 'market_rate', 'competitor_price']
        forecast = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'horizon': self.config.get('forecast_horizon', 30),
            'predictions': {}
        }

        for metric in pricing_metrics:
            if metric in self.market_metrics and self.market_metrics[metric]:
                values = [v['value'] for v in self.market_metrics[metric]]
                forecast['predictions'][metric] = self._forecast_values(
                    values, forecast['horizon']
                )

        return forecast

    def _forecast_demand(self) -> Dict[str, Any]:
        """Generate demand forecasts."""
        demand_metrics = ['volume', 'frequency', 'seasonality']
        forecast = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'horizon': self.config.get('forecast_horizon', 30),
            'predictions': {}
        }

        for metric in demand_metrics:
            if metric in self.market_metrics and self.market_metrics[metric]:
                values = [v['value'] for v in self.market_metrics[metric]]
                forecast['predictions'][metric] = self._forecast_values(
                    values, forecast['horizon']
                )

        return forecast

    def _forecast_conversion(self) -> Dict[str, Any]:
        """Generate conversion rate forecasts."""
        conversion_metrics = ['conversion_rate', 'bounce_rate', 'engagement']
        forecast = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'horizon': self.config.get('forecast_horizon', 30),
            'predictions': {}
        }

        for metric in conversion_metrics:
            if metric in self.market_metrics and self.market_metrics[metric]:
                values = [v['value'] for v in self.market_metrics[metric]]
                forecast['predictions'][metric] = self._forecast_values(
                    values, forecast['horizon']
                )

        return forecast

    def _calculate_correlations(self) -> Dict[str, float]:
        """Calculate correlations between market metrics."""
        correlations = {}
        metrics = list(self.market_metrics.keys())
        
        for i, metric1 in enumerate(metrics):
            for metric2 in metrics[i+1:]:
                if not (self.market_metrics[metric1] and self.market_metrics[metric2]):
                    continue
                    
                values1 = [v['value'] for v in self.market_metrics[metric1]]
                values2 = [v['value'] for v in self.market_metrics[metric2]]
                
                if len(values1) == len(values2) and len(values1) > 1:
                    correlation = self._calculate_correlation(values1, values2)
                    correlations[f'{metric1}__{metric2}'] = correlation

        return correlations

    def _detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalies in market metrics."""
        anomalies = []
        
        for metric, values in self.market_metrics.items():
            if len(values) < 10:
                continue
                
            recent_values = [v['value'] for v in values[-10:]]
            mean = statistics.mean(recent_values)
            std_dev = statistics.stdev(recent_values)
            
            latest = values[-1]['value']
            if abs(latest - mean) > 2 * std_dev:
                anomalies.append({
                    'metric': metric,
                    'timestamp': values[-1]['timestamp'],
                    'value': latest,
                    'expected_range': [mean - 2*std_dev, mean + 2*std_dev]
                })

        return anomalies

    def _detect_significant_changes(self, insights: Dict[str, Any]) -> bool:
        """Detect if there are significant market changes to report."""
        if insights.get('anomalies'):
            return True
            
        metrics = insights.get('metrics', {})
        for metric_data in metrics.values():
            if metric_data.get('trend') in ['strongly_increasing', 'strongly_decreasing']:
                return True
                
        return False

    def _broadcast_market_alert(self, insights: Dict[str, Any]) -> None:
        """Broadcast significant market changes to interested agents."""
        alert = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'type': 'market_alert',
            'changes': [],
            'anomalies': insights.get('anomalies', [])
        }

        # Add significant metric changes
        metrics = insights.get('metrics', {})
        for metric, data in metrics.items():
            if data.get('trend') in ['strongly_increasing', 'strongly_decreasing']:
                alert['changes'].append({
                    'metric': metric,
                    'trend': data['trend'],
                    'current_value': data['current']
                })

        self.send_message(
            None,
            'market.synthesis',
            alert,
            priority='high'
        )

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction and strength."""
        if len(values) < 2:
            return 'stable'
            
        changes = [b - a for a, b in zip(values[:-1], values[1:])]
        avg_change = statistics.mean(changes)
        std_dev = statistics.stdev(changes) if len(changes) > 1 else 0
        
        if abs(avg_change) < 0.1 * std_dev:
            return 'stable'
        elif abs(avg_change) > std_dev:
            return 'strongly_increasing' if avg_change > 0 else 'strongly_decreasing'
        else:
            return 'increasing' if avg_change > 0 else 'decreasing'

    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        n = len(x)
        if n != len(y) or n < 2:
            return 0.0
            
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        covariance = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        std_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
        std_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))
        
        if std_x == 0 or std_y == 0:
            return 0.0
            
        return covariance / (std_x * std_y)

    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility as coefficient of variation."""
        if not values or len(values) < 2:
            return 0.0
            
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values)
        
        if mean == 0:
            return 0.0
            
        return std_dev / abs(mean)

    def _identify_segments(self, threshold: float) -> List[Dict[str, Any]]:
        """Identify market segments based on metric clustering."""
        segments = []
        # Implementation would depend on specific segmentation requirements
        return segments

    def _identify_opportunities(
        self, 
        metrics: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify market opportunities from metrics."""
        opportunities = []
        
        for metric, data in metrics.items():
            if data['trend'] == 'strongly_increasing':
                opportunities.append({
                    'type': 'growth',
                    'metric': metric,
                    'potential': 'high',
                    'confidence': self._calculate_opportunity_confidence(data)
                })
                
        return opportunities

    def _calculate_adjustments(
        self, 
        current: float, 
        target: float
    ) -> List[Dict[str, Any]]:
        """Calculate required adjustments to reach target value."""
        adjustments = []
        difference = target - current
        
        if abs(difference) > 0.01 * current:  # 1% threshold
            adjustments.append({
                'type': 'relative',
                'change': difference / current,
                'absolute': difference
            })
            
        return adjustments

    def _generate_recommendations(
        self, 
        adjustments: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate strategic recommendations based on adjustments."""
        recommendations = []
        
        for metric, data in adjustments.items():
            if 'suggested_changes' in data:
                for change in data['suggested_changes']:
                    recommendations.append({
                        'metric': metric,
                        'type': change['type'],
                        'magnitude': abs(change['change']),
                        'direction': 'increase' if change['change'] > 0 else 'decrease'
                    })
                    
        return recommendations

    def _forecast_values(
        self, 
        values: List[float], 
        horizon: int
    ) -> List[float]:
        """Generate forecast values using simple moving average."""
        if not values:
            return []
            
        window = min(len(values), 5)  # 5-point moving average
        if window < 2:
            return [values[0]] * horizon
            
        weights = [1/window] * window
        ma = sum(v * w for v, w in zip(values[-window:], weights))
        
        return [ma] * horizon

    def _calculate_confidence_intervals(
        self, 
        predictions: List[float]
    ) -> Dict[str, List[float]]:
        """Calculate confidence intervals for predictions."""
        if not predictions:
            return {'lower': [], 'upper': []}
            
        std_dev = statistics.stdev(predictions) if len(predictions) > 1 else 0
        confidence = 1.96  # 95% confidence interval
        
        lower = [p - confidence * std_dev for p in predictions]
        upper = [p + confidence * std_dev for p in predictions]
        
        return {'lower': lower, 'upper': upper}

    def _calculate_forecast_confidence(
        self, 
        forecast: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for a forecast."""
        if not forecast or 'predictions' not in forecast:
            return 0.0
            
        # Simple confidence based on data availability and volatility
        confidence = 0.8  # Base confidence
        
        for metric, values in forecast['predictions'].items():
            if not values:
                confidence *= 0.8  # Reduce confidence for missing data
            elif len(values) > 1:
                volatility = self._calculate_volatility(values)
                confidence *= (1 - min(volatility, 0.5))  # Reduce confidence for high volatility
                
        return max(0.0, min(1.0, confidence))

    def _validate_forecast(self, forecast: Dict[str, Any]) -> Dict[str, Any]:
        """Validate forecast results."""
        validation = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics_validated': 0,
            'confidence_score': 0.0,
            'warnings': []
        }

        if not forecast or 'predictions' not in forecast:
            validation['warnings'].append('Empty forecast')
            return validation

        total_metrics = len(forecast['predictions'])
        if total_metrics == 0:
            validation['warnings'].append('No metrics in forecast')
            return validation

        validation['metrics_validated'] = total_metrics
        validation['confidence_score'] = self._calculate_forecast_confidence(forecast)

        return validation
